import graphene

import battles.schema
import users.schema


class Query(users.schema.Query, battles.schema.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
