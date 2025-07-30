import os
from typing import Dict, Any
from dotenv import load_dotenv

# 加载配置文件
# 优先加载 .env 文件，如果没有则加载 config.env
if os.path.exists('.env'):
    load_dotenv('.env')
elif os.path.exists('config.env'):
    load_dotenv('config.env')
else:
    print("警告：未找到配置文件 .env 或 config.env")

class Config:
    """配置类"""
    
    # 数据库配置 - 从环境变量读取，避免敏感信息泄露
    DATABASE = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),  # 必须通过环境变量设置
        'database': os.getenv('DB_NAME', 'flight_guarantee'),
        'charset': os.getenv('DB_CHARSET', 'utf8mb4'),
        'hostname': os.getenv('DB_HOSTNAME', 'localhost'),
        'version': os.getenv('DB_VERSION', '8.0.43'),
        'datadir': os.getenv('DB_DATADIR', '')
    }
    
    # 模型配置
    MODEL = {
        'random_state': 42,
        'test_size': 0.2,
        'cv_folds': 5,
        'n_jobs': -1
    }
    
    # XGBoost参数
    XGBOOST_PARAMS = {
        'n_estimators': [100, 200, 300],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1, 0.2],
        'subsample': [0.8, 0.9, 1.0],
        'colsample_bytree': [0.8, 0.9, 1.0],
        'objective': 'reg:squarederror',
        'eval_metric': 'rmse'
    }
    
    # LightGBM参数
    LIGHTGBM_PARAMS = {
        'n_estimators': [100, 200, 300],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1, 0.2],
        'subsample': [0.8, 0.9, 1.0],
        'colsample_bytree': [0.8, 0.9, 1.0],
        'objective': 'regression',
        'metric': 'rmse',
        'verbose': -1
    }
    
    # CatBoost参数
    CATBOOST_PARAMS = {
        'iterations': [100, 200, 300],
        'depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1, 0.2],
        'subsample': [0.8, 0.9, 1.0],
        'loss_function': 'RMSE',
        'verbose': False
    }
    
    # 特征配置
    FEATURES = {
        'target_column': 'cv',#主要目标变量
        'feature_columns': [
            # 任务本质特征（高影响）
            'task_type_encoded',        # 任务类型
            
            # 环境约束特征（高影响）
            'visibility',               # 能见度
            'wind_speed',              # 风速
            'temperature',             # 温度
            'weather_severity',        # 天气严重程度
            
            # 时间压力特征（高影响）
            'dep_delay',               # 起飞延误
            'arr_delay',               # 到达延误
            'ready_delay',             # 准备延误
            'start_delay',             # 开始延误
            'end_delay',               # 结束延误
            
            # 运营状态特征（中高影响）
            'status_encoded',          # 航班状态
            'is_delayed',             # 是否延误
            'is_cancelled',           # 是否取消
            'is_early',               # 是否提前
            
            # 人员能力特征（中影响）
            'skill_level_encoded',     # 技能等级
            
            # 时间模式特征（中影响）
            'hour',                    # 小时
            'day_of_week',            # 星期几
            'is_holiday',             # 是否节假日
            'time_period_encoded',    # 时段
        ],
        
        # 归因分析特征（不用于预测，仅用于归因分析）
        'attribution_features': [
            'cv_flight',              # 航班级别CV值
            'cv_task',                # 任务类型级别CV值
            'cv_airline',             # 航空公司级别CV值
            'cv_hour',                # 时间维度CV值
        ]
    }
    
    # 路径配置
    PATHS = {
        'models': 'models/',
        'data': 'data/',
        'logs': 'logs/',
        'reports': 'reports/',
        'plots': 'plots/'
    }
    
    # API配置
    API = {
        'host': '0.0.0.0',
        'port': 8000,
        'debug': True,
        'reload': True
    }
    
    # 日志配置
    LOGGING = {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': 'logs/app.log'
    }
    
    # CV阈值配置
    CV_THRESHOLDS = {
        'very_low': 0.1,      # 波动性很小
        'low': 0.2,           # 波动性较小
        'medium': 0.3,        # 波动性中等
        'high': float('inf')  # 波动性较大
    }
    
    @classmethod
    def get_database_url(cls) -> str:
        """获取数据库连接URL"""
        db = cls.DATABASE
        return f"mysql+pymysql://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}"
    
    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """获取数据库连接配置"""
        return {
            'host': cls.DATABASE['host'],
            'port': cls.DATABASE['port'],
            'user': cls.DATABASE['user'],
            'password': cls.DATABASE['password'],
            'database': cls.DATABASE['database'],
            'charset': cls.DATABASE['charset']
        }
    
    @classmethod
    def create_directories(cls):
        """创建必要的目录"""
        for path in cls.PATHS.values():
            os.makedirs(path, exist_ok=True)
    
    @classmethod
    def get_model_params(cls, model_name: str) -> Dict[str, Any]:
        """获取模型参数"""
        params_map = {
            'xgboost': cls.XGBOOST_PARAMS,
            'lightgbm': cls.LIGHTGBM_PARAMS,
            'catboost': cls.CATBOOST_PARAMS
        }
        return params_map.get(model_name.lower(), {})
    
    @classmethod
    def get_cv_level(cls, cv_value: float) -> str:
        """根据CV值判断波动性级别"""
        if cv_value < cls.CV_THRESHOLDS['very_low']:
            return "波动性很小"
        elif cv_value < cls.CV_THRESHOLDS['low']:
            return "波动性较小"
        elif cv_value < cls.CV_THRESHOLDS['medium']:
            return "波动性中等"
        else:
            return "波动性较大"
    
    @classmethod
    def get_connection_info(cls) -> Dict[str, str]:
        """获取连接信息用于分享"""
        return {
            'host': cls.DATABASE['host'],
            'port': str(cls.DATABASE['port']),
            'database': cls.DATABASE['database'],
            'user': cls.DATABASE['user'],
            'charset': cls.DATABASE['charset'],
            'hostname': cls.DATABASE['hostname'],
            'version': cls.DATABASE['version'],
            'datadir': cls.DATABASE['datadir']
        } 