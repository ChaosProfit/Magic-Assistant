# from threading import Lock
# import psycopg2
# from loguru import logger
# from magic_assistant.db.base_sql_db import BaseSqlDb
#
# class Postgre(BaseSqlDb):
#     def __init__(self):
#         self._conn = None
#         self._param = None
#         self._select_lock: Lock = Lock()
#         self._insert_lock: Lock = Lock()
#         self._delete_lock: Lock = Lock()
#         self._update_lock: Lock = Lock()
#         self._insert_many_lock: Lock = Lock()
#
#     def init(self, param):
#         """
#         init
#         """
#         self._param = param
#         try:
#
#             self._conn = psycopg2.connect(database=param.database, user=param.user, password=param.password, host=param.host, port=param.port)
#             logger.debug("postgre init suc")
#             return 0
#         except Exception as e:
#             logger.error("connect postgre failed")
#             return -1
#
#     def exit(self):
#         if self._conn is not None:
#             self._conn.commit()
#             self._conn.close()
#
#     def _roll_back(self):
#         try:
#             self._conn.rollback()
#         except psycopg2.InterfaceError:
#             logger.error('connect closed, and going to restart to rollback')
#             ret = self.init(self._param)
#             if ret == 0:
#                 self._conn.rollback()
#
#     def insert(self, insert_sql):
#         """
#         insert
#         """
#         self._insert_lock.acquire()
#         try:
#             with self._conn.cursor() as cursor:
#                 cursor.execute(insert_sql)
#             self._conn.commit()
#             logger.debug('insert suc')
#             return 0
#
#         except Exception as error:
#             logger.error("catch exception: %s" % str(error))
#             logger.error("insert_sql: %s" % insert_sql)
#
#             self._roll_back()
#             try:
#                 with self._conn.cursor() as cursor:
#                     cursor.execute(insert_sql)
#                 self._conn.commit()
#             except Exception as error2:
#                 logger.error("catch exception: %s" % str(error2))
#                 logger.error("insert_sql: %s" % insert_sql)
#                 return -1
#
#             return 0
#         finally:
#             self._insert_lock.release()
#
#     def update(self, update_sql):
#         """
#         update
#         """
#         self._update_lock.acquire()
#         try:
#             with self._conn.cursor() as cursor:
#                 cursor.execute(update_sql)
#             self._conn.commit()
#             logger.debug('update suc')
#             return 0
#         except Exception as error:
#             # self._conn.rollback()
#             self._roll_back()
#             try:
#                 with self._conn.cursor() as cursor:
#                     cursor.execute(update_sql)
#                 self._conn.commit()
#                 logger.debug('update suc')
#                 return 0
#             except Exception as error:
#                 logger.error("catch exception: %s" % str(error))
#                 logger.error("updateSql: %s" % update_sql)
#             return -1
#         finally:
#             self._update_lock.release()
#
#     def delete(self, delete_sql, args=()):
#         """
#         delete
#         """
#         self._delete_lock.acquire()
#         try:
#             with self._conn.cursor() as cursor:
#                 cursor.execute(delete_sql, args)
#             self._conn.commit()
#             logger.debug("delete suc")
#             return 0
#         except Exception as error:
#             # self._conn.rollback()
#             self._roll_back()
#             try:
#                 with self._conn.cursor() as cursor:
#                     cursor.execute(delete_sql, args)
#                 self._conn.commit()
#             except Exception as error:
#                 logger.error("catch exception: %s" % str(error))
#                 logger.error("delete_sql: %s" % delete_sql)
#             return -1
#
#         finally:
#             self._delete_lock.release()
#
#     def select(self, select_sql, args=()):
#         """
#         select
#         """
#         self._select_lock.acquire()
#         try:
#             with self._conn.cursor() as cursor:
#                 cursor.execute(select_sql, args)
#                 results = cursor.fetchall()
#             return results
#         except Exception as error:
#             self._roll_back()
#             try:
#                 with self._conn.cursor() as cursor:
#                     cursor.execute(select_sql, args)
#                     results = cursor.fetchall()
#                 return results
#             except Exception as error:
#                 logger.error("select_sql:%s" % select_sql)
#                 logger.error("catch exception: %s" % str(error))
#             return []
#         finally:
#             self._select_lock.release()