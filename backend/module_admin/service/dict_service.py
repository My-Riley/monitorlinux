from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.enums import RedisInitKeyConfig
from module_admin.entity.do.dict_do import SysDictData, SysDictType
from utils.log_util import logger


class DictDataService:
    """字典数据服务层"""

    @classmethod
    async def init_cache_sys_dict_services(cls, db: AsyncSession, redis):
        """初始化缓存字典数据"""
        logger.info("🔎 初始化字典缓存...")
        try:
            # 获取所有字典类型
            dict_type_query = select(SysDictType).where(SysDictType.status == "0")
            dict_type_result = await db.execute(dict_type_query)
            dict_types = dict_type_result.scalars().all()

            for dict_type in dict_types:
                # 获取字典数据
                dict_data_query = (
                    select(SysDictData)
                    .where(SysDictData.dict_type == dict_type.dict_type, SysDictData.status == "0")
                    .order_by(SysDictData.dict_sort)
                )
                dict_data_result = await db.execute(dict_data_query)
                dict_data_list = dict_data_result.scalars().all()

                # 缓存到Redis
                if dict_data_list:
                    cache_data = [
                        {
                            "dictCode": item.dict_code,
                            "dictSort": item.dict_sort,
                            "dictLabel": item.dict_label,
                            "dictValue": item.dict_value,
                            "dictType": item.dict_type,
                            "cssClass": item.css_class,
                            "listClass": item.list_class,
                            "isDefault": item.is_default,
                            "status": item.status,
                            "remark": item.remark,
                        }
                        for item in dict_data_list
                    ]
                    import json

                    await redis.set(
                        f"{RedisInitKeyConfig.SYS_DICT.key}:{dict_type.dict_type}",
                        json.dumps(cache_data, ensure_ascii=False),
                    )
            logger.info("✅️ 字典缓存初始化成功")
        except Exception as e:
            logger.error(f"❌️ 字典缓存初始化失败: {e}")

    @classmethod
    async def query_dict_data_list_from_cache_services(cls, redis, dict_type: str):
        """
        从缓存中获取字典数据列表
        """
        import json

        cache_key = f"{RedisInitKeyConfig.SYS_DICT.key}:{dict_type}"
        cache_data = await redis.get(cache_key)
        if cache_data:
            return json.loads(cache_data)
        return []
