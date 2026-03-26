from fastapi import Request

from config.enums import RedisInitKeyConfig
from config.get_redis import RedisUtil
from module_admin.entity.vo.cache_vo import CacheInfoModel, CacheMonitorModel
from module_admin.entity.vo.common_vo import CrudResponseModel


class CacheService:
    """
    缓存监控模块服务层
    """

    @classmethod
    async def get_cache_monitor_statistical_info_services(cls, request: Request):
        """
        获取缓存监控信息
        """
        info = await request.app.state.redis.info()
        db_size = await request.app.state.redis.dbsize()
        command_stats_dict = await request.app.state.redis.info("commandstats")
        command_stats = []
        if command_stats_dict:
            for key, value in command_stats_dict.items():
                if "_" in key:
                    command_stats.append(dict(name=key.split("_")[1], value=str(value.get("calls"))))
        result = CacheMonitorModel(commandStats=command_stats, dbSize=db_size, info=info)

        return result

    @classmethod
    async def get_cache_monitor_cache_name_services(cls):
        """
        获取缓存名称列表信息
        """
        name_list = []
        for key_config in RedisInitKeyConfig:
            name_list.append(
                CacheInfoModel(
                    cacheKey="",
                    cacheName=key_config.key,
                    cacheValue="",
                    remark=key_config.remark,
                )
            )

        return name_list

    @classmethod
    async def get_cache_monitor_cache_key_services(cls, request: Request, cache_name: str):
        """
        获取缓存键名列表信息
        """
        cache_keys = await request.app.state.redis.keys(f"{cache_name}*")

        final_list = []
        for key in cache_keys:
            if key.startswith(f"{cache_name}:"):
                parts = key.split(":", 1)
                if len(parts) > 1:
                    final_list.append(parts[1])

        return final_list

    @classmethod
    async def get_cache_monitor_cache_value_services(cls, request: Request, cache_name: str, cache_key: str):
        """
        获取缓存内容信息
        """
        cache_value = await request.app.state.redis.get(f"{cache_name}:{cache_key}")

        return CacheInfoModel(cacheKey=cache_key, cacheName=cache_name, cacheValue=cache_value, remark="")

    @classmethod
    async def clear_cache_monitor_cache_name_services(cls, request: Request, cache_name: str):
        """
        清除缓存名称对应所有键值
        """
        cache_keys = await request.app.state.redis.keys(f"{cache_name}*")
        if cache_keys:
            await request.app.state.redis.delete(*cache_keys)

        return CrudResponseModel(is_success=True, message=f"{cache_name}对应键值清除成功")

    @classmethod
    async def clear_cache_monitor_cache_key_services(cls, request: Request, cache_name: str, cache_key: str):
        """
        清除缓存名称对应所有键值
        """
        # 删除特定的 key: cache_name:cache_key
        # 前端传来的 cache_key 只是后缀，需要拼接
        target_key = f"{cache_name}:{cache_key}"
        await request.app.state.redis.delete(target_key)

        return CrudResponseModel(is_success=True, message=f"{target_key}键值清除成功")

    @classmethod
    async def clear_cache_monitor_all_services(cls, request: Request):
        """
        清除所有缓存
        """
        cache_keys = await request.app.state.redis.keys()
        if cache_keys:
            await request.app.state.redis.delete(*cache_keys)

        await RedisUtil.init_sys_dict(request.app.state.redis)
        await RedisUtil.init_sys_config(request.app.state.redis)

        return CrudResponseModel(is_success=True, message="所有缓存清除成功")
