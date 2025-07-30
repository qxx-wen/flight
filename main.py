from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
import uvicorn
import logging
import os
from src.models.model_trainer import ModelTrainer
from src.models.attribution_analyzer import AttributionAnalyzer
from src.data.data_processor import DataProcessor
from src.utils.config import Config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局变量
model_trainer = None
attribution_analyzer = None
data_processor = None

# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    global model_trainer, attribution_analyzer, data_processor
    
    try:
        logger.info("初始化系统组件...")
        
        # 初始化数据处理器
        data_processor = DataProcessor()
        
        # 初始化模型训练器
        model_trainer = ModelTrainer()
        
        # 初始化归因分析器
        attribution_analyzer = AttributionAnalyzer()
        
        logger.info("系统初始化完成")
        
    except Exception as e:
        logger.error(f"系统初始化失败: {str(e)}")
        raise e
    
    yield
    
    # 关闭时执行（如果需要清理资源）
    logger.info("系统关闭，清理资源...")

# 创建FastAPI应用
app = FastAPI(
    title="航班归因分析系统",
    description="分析航班保障任务CV波动性的归因分析系统",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建plots目录并挂载静态文件服务
plots_dir = Config.PATHS.get('plots', 'plots')
os.makedirs(plots_dir, exist_ok=True)
app.mount("/plots", StaticFiles(directory=plots_dir), name="plots")

class TaskIdRequest(BaseModel):
    task_id: int

class TimeRangeRequest(BaseModel):
    start_time: str  # 格式: "2024-01-01 08:00:00"
    end_time: str    # 格式: "2024-01-01 12:00:00"

class AttributionResponse(BaseModel):
    shap_values: Dict[str, float]
    feature_importance: List[Dict[str, Any]]  # 改为Any以支持字符串特征名
    top_features: List[Dict[str, Any]]  # 改为Any以支持字符串特征名
    data_summary: Dict[str, Any]
    plots: Dict[str, str]  # 新增：图片路径
    message: str

class ModelInfoResponse(BaseModel):
    type: str
    training_date: str
    feature_count: int
    performance: Dict[str, float]

# API路由
@app.get("/")
async def root():
    return {"message": "航班归因分析系统API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "系统运行正常"}



@app.post("/api/v1/attribution/task", response_model=AttributionResponse)
async def attribution_analysis_by_task(request: TaskIdRequest):
    """
    根据任务ID进行归因分析
    """
    try:
        # 根据任务ID获取数据
        task_data = data_processor.load_data_by_task_id(request.task_id)
        
        if task_data.empty:
            raise HTTPException(status_code=404, detail=f"任务ID {request.task_id} 没有找到数据")
        
        # 执行归因分析并生成SHAP图
        result = attribution_analyzer.analyze_with_plots(task_data)
        
        return AttributionResponse(
            shap_values=result['feature_importance'],
            feature_importance=[{'feature': k, 'importance': v} for k, v in result['top_features']],
            top_features=[{'feature': k, 'importance': v} for k, v in result['top_features']],
            data_summary={
                'task_id': request.task_id,
                'total_samples': len(task_data),
                'feature_count': len(result['feature_importance'])
            },
            plots=result['plots'],  # 新增：返回图片路径
            message=f"任务ID {request.task_id} 归因分析完成，SHAP图已生成"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"任务归因分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"归因分析失败: {str(e)}")

@app.post("/api/v1/attribution/time", response_model=AttributionResponse)
async def attribution_analysis_by_time(request: TimeRangeRequest):
    """
    根据时间段进行归因分析
    """
    try:
        # 根据时间段获取数据
        time_data = data_processor.load_data_by_time_range(request.start_time, request.end_time)
        
        if time_data.empty:
            raise HTTPException(status_code=404, detail=f"时间段 {request.start_time} 到 {request.end_time} 没有找到数据")
        
        # 执行归因分析并生成SHAP图
        result = attribution_analyzer.analyze_with_plots(time_data)
        
        return AttributionResponse(
            shap_values=result['feature_importance'],
            feature_importance=[{'feature': k, 'importance': v} for k, v in result['top_features']],
            top_features=[{'feature': k, 'importance': v} for k, v in result['top_features']],
            data_summary={
                'start_time': request.start_time,
                'end_time': request.end_time,
                'total_samples': len(time_data),
                'feature_count': len(result['feature_importance'])
            },
            plots=result['plots'],  # 新增：返回图片路径
            message=f"时间段 {request.start_time} 到 {request.end_time} 归因分析完成，SHAP图已生成"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"时间段归因分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"归因分析失败: {str(e)}")

@app.post("/api/v1/train")
async def train_model():
    """
    训练模型（使用全部数据）
    """
    try:
        # 加载和预处理数据
        data = data_processor.load_and_preprocess()
        
        # 训练模型
        best_model, metrics = model_trainer.train(data)
        
        return {
            "message": "模型训练完成",
            "best_model": best_model,
            "metrics": metrics,
            "training_samples": len(data[0]),  # X_train
            "test_samples": len(data[1])       # X_test
        }
        
    except Exception as e:
        logger.error(f"模型训练失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"模型训练失败: {str(e)}")

@app.get("/api/v1/model/info", response_model=ModelInfoResponse)
async def get_model_info():
    """
    获取模型信息
    """
    try:
        model_info = model_trainer.get_model_info()
        
        return ModelInfoResponse(
            type=model_info.get('best_model', '未知'),
            training_date=model_info.get('training_date', '未知'),
            feature_count=model_info.get('feature_count', 0),
            performance=model_info.get('metrics', {})
        )
        
    except Exception as e:
        logger.error(f"获取模型信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取模型信息失败: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 