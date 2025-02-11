from django.conf import settings 
from utils.redis_client import RedisClient 
from utils.redis_serializers import DjangoModelSerializer 


class RedisHelper:

    @classmethod 
    def _load_objects_to_cache(cls, key, objects):
        conn = RedisClient.get_connection()
        serialized_list = [] 

        # 最多只 cache REDIS_LIST_LENGTH_LIMIT 那么多个 objects
        # 超过这个限制的 objects，就去数据库里读取。一般这个限制会比较大，比如 1000
        # 因此翻页翻到 1000 的用户访问量会比较少，从数据库读取也不是大问题
        for obj in objects[:settings.REDIS_LIST_LENGTH_LIMIT]:
            serialized_data = DjangoModelSerializer.serialize(obj)
            serialized_list.append(serialized_data) 

        if serialized_list:
            #The RPUSH command in Redis is used to append one or more elements to the end of a list stored at a given key. If the key does not exist, Redis will create a new list and add the provided elements to it.
            conn.rpush(key, *serialized_list)
            #The EXPIRE command in Redis is used to set a time-to-live (TTL) for a key, after which the key will automatically be deleted from the database.
            conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)

    @classmethod
    def load_objects(cls, key, queryset):
        conn = RedisClient.get_connection()
        # if key exist in cache, read it 
        if conn.exists(key):
            serialized_list = conn.lrange(key, 0, -1)
            objects = []
            for serialized_data in serialized_list:
                deserialized_obj = DjangoModelSerializer.deserialize(serialized_data)
                objects.append(deserialized_obj)
            return objects 
        
        cls._load_objects_to_cache(key, queryset) 
    
        # 转换为 list 的原因是保持返回类型的统一，因为存在 redis 里的数据是 list 的形式
        return list(queryset)
    
    @classmethod
    def push_object(cls, key, obj, queryset):
        conn = RedisClient.get_connection()
        if not conn.exists(key):
            # if key don't exist, load from database 
            cls._load_objects_to_cache(key, queryset)
            return 
        serialized_data = DjangoModelSerializer.serialize(obj)
        conn.lpush(key, serialized_data)
        conn.ltrim(key, 0, settings.REDIS_LIST_LENGTH_LIMIT - 1)

    @classmethod
    def get_count_key(cls, obj, attr):
        return "{}.{}:{}".format(obj.__class__.__name__, attr, obj.id) 
    
    
