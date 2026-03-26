from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.enums import RedisInitKeyConfig
from module_admin.entity.do.config_do import SysConfig
from utils.log_util import logger


class ConfigService:
    """参数配置服务层"""

    @classmethod
    async def init_cache_sys_config_services(cls, db: AsyncSession, redis):
        """初始化缓存参数配置"""
        logger.info("🔎 初始化参数配置缓存...")
        try:
            # 获取所有参数配置
            config_query = select(SysConfig)
            config_result = await db.execute(config_query)
            configs = config_result.scalars().all()

            for config in configs:
                await redis.set(f"{RedisInitKeyConfig.SYS_CONFIG.key}:{config.config_key}", config.config_value)
            logger.info("✅️ 参数配置缓存初始化成功")
        except Exception as e:
            logger.error(f"❌️ 参数配置缓存初始化失败: {e}")
