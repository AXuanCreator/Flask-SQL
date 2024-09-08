from Config import BookCategory, ReturnCode, db


class BookCategoryServices:
    @staticmethod
    def insert_book_category(name_data):
        if BookCategory.query.filter_by(name=name_data).first():
            return ReturnCode.CATEGORY_EXIST

        new_book_category = BookCategory(name=name_data, quantity=0)
        db.session.add(new_book_category)
        db.session.commit()

        return ReturnCode.SUCCESS

    @staticmethod
    def list_book_categories(page, per_page):
        """展示某个分页的书籍"""
        # 获取总记录数
        categories_query = BookCategory.query
        total = categories_query.count()

        # 获取该分页的内容
        categories = categories_query.offset((page - 1) * per_page).limit(per_page).all()
        return categories, total

    @staticmethod
    def get_book_category_by_name(name):
        """根据名字搜索类别"""
        return BookCategory.query.filter_by(name=name).first()

    # 类别信息更新
    @staticmethod
    def update_book_category(id, category_name):
        # TODO:当书籍旧分类下拥有书籍时，更新失败
        category = BookCategory.query.get(id)
        if category is None or category_name is None:
            return ReturnCode.FAIL

        category.name = category_name
        db.session.commit()

        return ReturnCode.SUCCESS

    # 类别删除
    @staticmethod
    def delete_book_category(id):
        # TODO:当书籍分类下拥有书籍时，不允许删除
        category = BookCategory.query.get(id)
        if category is None:
            return ReturnCode.CATEGORY_NOT_EXIST

        db.session.delete(category)
        db.session.commit()
        return ReturnCode.SUCCESS
