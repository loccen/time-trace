"""
基础数据访问对象
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic
from datetime import datetime

from app.core.database import db_manager
from app.core.logger import get_logger

logger = get_logger("DAO")

T = TypeVar('T')


class BaseDAO(ABC, Generic[T]):
    """基础DAO抽象类"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.db = db_manager
    
    @abstractmethod
    def _row_to_model(self, row: Dict[str, Any]) -> T:
        """将数据库行转换为模型对象"""
        pass
    
    def get_by_id(self, record_id: int) -> Optional[T]:
        """根据ID获取记录"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE id = ?"
            rows = self.db.execute_query(query, (record_id,))
            
            if rows:
                return self._row_to_model(rows[0])
            return None
            
        except Exception as e:
            logger.error(f"获取记录失败，表: {self.table_name}, ID: {record_id}, 错误: {e}")
            raise
    
    def delete(self, record_id: int) -> bool:
        """删除记录"""
        try:
            query = f"DELETE FROM {self.table_name} WHERE id = ?"
            affected_rows = self.db.execute_update(query, (record_id,))
            
            success = affected_rows > 0
            if success:
                logger.info(f"删除记录成功，表: {self.table_name}, ID: {record_id}")
            else:
                logger.warning(f"删除记录失败，记录不存在，表: {self.table_name}, ID: {record_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"删除记录失败，表: {self.table_name}, ID: {record_id}, 错误: {e}")
            raise
    
    def exists(self, record_id: int) -> bool:
        """检查记录是否存在"""
        try:
            query = f"SELECT 1 FROM {self.table_name} WHERE id = ? LIMIT 1"
            rows = self.db.execute_query(query, (record_id,))
            return len(rows) > 0
        except Exception as e:
            logger.error(f"检查记录存在性失败，表: {self.table_name}, ID: {record_id}, 错误: {e}")
            return False
    
    def count_all(self) -> int:
        """统计总记录数"""
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name}"
            rows = self.db.execute_query(query)
            return rows[0]['count'] if rows else 0
        except Exception as e:
            logger.error(f"统计记录数失败，表: {self.table_name}, 错误: {e}")
            return 0
    
    def get_all(self, limit: int = None, offset: int = None) -> List[T]:
        """获取所有记录"""
        try:
            query = f"SELECT * FROM {self.table_name}"
            params = []
            
            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)
                
                if offset is not None:
                    query += " OFFSET ?"
                    params.append(offset)
            
            rows = self.db.execute_query(query, tuple(params))
            return [self._row_to_model(row) for row in rows]
            
        except Exception as e:
            logger.error(f"获取所有记录失败，表: {self.table_name}, 错误: {e}")
            raise
    
    def execute_custom_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """执行自定义查询"""
        try:
            return self.db.execute_query(query, params)
        except Exception as e:
            logger.error(f"执行自定义查询失败: {query}, 参数: {params}, 错误: {e}")
            raise
    
    def begin_transaction(self):
        """开始事务"""
        return self.db.begin_transaction()


class TimestampMixin:
    """时间戳混入类"""
    
    def add_timestamps(self, data: Dict[str, Any], is_update: bool = False) -> Dict[str, Any]:
        """添加时间戳"""
        now = datetime.now().isoformat()
        
        if not is_update:
            data['created_at'] = now
        
        data['updated_at'] = now
        return data
    
    def build_update_query(self, table_name: str, update_data: Dict[str, Any], 
                          record_id: int) -> tuple:
        """构建更新查询"""
        # 添加更新时间戳
        update_data = self.add_timestamps(update_data, is_update=True)
        
        # 构建SET子句
        set_clauses = []
        params = []
        
        for field, value in update_data.items():
            set_clauses.append(f"{field} = ?")
            params.append(value)
        
        # 添加WHERE条件
        params.append(record_id)
        
        query = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE id = ?"
        return query, tuple(params)
