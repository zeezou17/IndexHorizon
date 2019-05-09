global Constants


class Constants(object):
    CREATE_HYPO_INDEX = "SELECT indexrelid FROM hypopg_create_index('CREATE INDEX ON  {0}({1})')"
    REMOVE_HYPO_INDEX = "select * from hypopg_drop_index({0})"
    REMOVE_ALL_HYPO_INDEXES = "select * from  hypopg_reset()"
    MULTI_KEY_CONCATENATION_STRING = '::'

    def __setattr__(self, *_):
        pass


Constants = Constants()


