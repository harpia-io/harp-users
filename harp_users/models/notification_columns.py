import traceback
from microservice_template_core import db
from marshmallow import Schema, fields, validate
from microservice_template_core.tools.logger import get_logger

logger = get_logger()


class NotificationColumns(db.Model):
    __tablename__ = 'harp_notification_columns'

    column_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    column_name = db.Column(db.VARCHAR(70), nullable=False, unique=True)

    def __repr__(self):
        return f"{self.column_id}_{self.column_name}"

    def dict(self):
        return {
            'column_id': self.column_id,
            'column_name': self.column_name,
        }

    @classmethod
    def get_all_columns(cls):
        all_columns = {}
        get_all_columns = cls.query.filter_by().all()

        for single_env in get_all_columns:
            all_columns[int(single_env.dict()['column_id'])] = single_env.dict()['column_name']

        print(all_columns)

        return all_columns

    @classmethod
    def add_new_column(cls, column_name):
        exist_column = cls.query.filter_by(column_name=column_name).one_or_none()
        if exist_column:
            raise ValueError(f"{column_name} already exist")

        new_obj = NotificationColumns(
            column_name=column_name
        )
        new_obj = new_obj.save()
        return new_obj

    def update_existing_column(self, column_id, new_column_name):

        self.query.filter_by(column_id=column_id).update({"column_name": new_column_name})

        db.session.commit()

    @classmethod
    def obj_exist(cls, column_id):
        return cls.query.filter_by(column_id=column_id).one_or_none()

    def save(self):
        try:
            db.session.add(self)
            db.session.flush()
            db.session.commit()

            return self
        except Exception as exc:
            logger.critical(
                msg=f"Can't commit changes to DB \nException: {str(exc)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}}
            )
            db.session.rollback()

    def delete_obj(self):
        db.session.delete(self)
        db.session.commit()


class NotificationColumnsSchema(Schema):
    column_id = fields.Int(dump_only=True)
    column_name = fields.Str(required=False)
