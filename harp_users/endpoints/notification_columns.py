# from microservice_template_core.tools.flask_restplus import api
# from flask_restx import Resource
# import traceback
# from microservice_template_core.tools.logger import get_logger
# from harp_users.models.notification_columns import NotificationColumns, NotificationColumnsSchema
# from flask import request
# from werkzeug.exceptions import NotFound, BadRequest
#
# logger = get_logger()
# ns = api.namespace('api/v1/notification-columns', description='Harp All notification columns endpoints')
# notification_columns = NotificationColumnsSchema()
#
#
# @ns.route('')
# class NotificationColumnsAPI(Resource):
#     @staticmethod
#     @api.response(200, 'New column has been added')
#     @api.response(400, 'Column already exist')
#     @api.response(500, 'Unexpected error on backend side')
#     def put():
#         """
#         Add new notification column
#         Use this method to add new notification column
#         * Send a JSON object
#         ```
#             {
#                 "column_name": "notification_output",
#             }
#         ```
#         """
#         try:
#             data = notification_columns.load(request.get_json())
#             new_obj = NotificationColumns.add_new_column(column_name=data['column_name'])
#             result = notification_columns.dump(new_obj.dict())
#             print(result)
#         except ValueError as val_exc:
#             logger.warning(
#                 msg=str(val_exc),
#                 extra={'tags': {}})
#             return {"msg": str(val_exc)}, 400
#         except Exception as exc:
#             logger.critical(
#                 msg=f"General exception \nException: {str(exc)} \nTraceback: {traceback.format_exc()}",
#                 extra={'tags': {}})
#             return {'msg': 'Exception raised. Check logs for additional info'}, 500
#
#         return result, 200
#
#     @staticmethod
#     @api.response(200, 'Column has been update')
#     @api.response(400, 'Column already exist')
#     @api.response(500, 'Unexpected error on backend side')
#     def post():
#         """
#         Update existing notification columns
#         Use this method to update existing notification columns
#         * Send a JSON object
#         ```
#             {
#                 "column_id": 12,
#                 "new_column_name": "notification_output_new",
#             }
#         ```
#         """
#         data = request.get_json()
#
#         print(data)
#
#         if 'column_id' not in data:
#             raise NotFound('column_id should be specified')
#
#         obj = NotificationColumns.obj_exist(column_id=data['column_id'])
#
#         if not obj:
#             raise NotFound('Column with specified id is not exist')
#         try:
#             obj.update_existing_column(column_id=data['column_id'], new_column_name=data['new_column_name'])
#             result = notification_columns.dump(obj.dict())
#         except ValueError as val_exc:
#             logger.warning(
#                 msg=f"Column updating exception \nException: {str(val_exc)} \nTraceback: {traceback.format_exc()}",
#                 extra={'tags': {}})
#             return {"msg": str(val_exc)}, 400
#         except BadRequest as bad_request:
#             logger.warning(
#                 msg=f"Column updating exception \nException: {str(bad_request)} \nTraceback: {traceback.format_exc()}",
#                 extra={'tags': {}})
#             return {'msg': str(bad_request)}, 400
#         except Exception as exc:
#             logger.critical(
#                 msg=f"Column updating exception \nException: {str(exc)} \nTraceback: {traceback.format_exc()}",
#                 extra={'tags': {}})
#             return {'msg': 'Exception raised. Check logs for additional info'}, 500
#         return result, 200
#
#     @staticmethod
#     def get():
#         """
#             Get all available columns
#         """
#         obj = NotificationColumns.get_all_columns()
#         if not obj:
#             raise NotFound('There are no any columns in table')
#
#         return obj, 200
#
#     @staticmethod
#     def delete():
#         """
#         Delete Notification column with specified id
#         * Send a JSON object
#         ```
#             {
#                 "column_id": 12
#             }
#         ```
#         """
#
#         data = request.get_json()
#
#         if 'column_id' not in data:
#             raise NotFound('column_id should be specified in JSON Payload')
#
#         obj = NotificationColumns.obj_exist(column_id=data['column_id'])
#
#         try:
#             if obj:
#                 obj.delete_obj()
#                 logger.info(
#                     msg=f"Column deletion. Id: {data['column_id']}",
#                     extra={})
#             else:
#                 raise NotFound(f'Object with specified column_id: {data["column_id"]} is not found')
#         except Exception as exc:
#             logger.critical(
#                 msg=f"Column deletion exception \nException: {str(exc)} \nTraceback: {traceback.format_exc()}",
#                 extra={'tags': {}})
#             return {'msg': f'Deletion of column with id: {data["column_id"]} failed. '
#                            f'Exception: {str(exc)}'}, 500
#         return {'msg': f"Column with id: {data['column_id']} successfully deleted"}, 200
