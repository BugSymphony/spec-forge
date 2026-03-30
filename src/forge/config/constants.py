from enum import Enum


class Stage(str, Enum):
    CONST = "constitution"
    SPEC = "specify"
    CLARIFY = "clarify"
    PLAN = "plan"
    TASKS = "tasks"
    IMPL = "implement"

    @classmethod
    def values(cls):
        return list(dict.fromkeys(e.value for e in cls))


STAGE_NAMES = [stage.value for stage in Stage]

STAGE_DEPENDENCIES = {
    Stage.SPEC: [],
    Stage.CLARIFY: [Stage.SPEC],
    Stage.PLAN: [Stage.SPEC],
    Stage.TASKS: [Stage.SPEC, Stage.PLAN],
    Stage.IMPL: [Stage.SPEC, Stage.PLAN, Stage.TASKS]
}


class ContentType(str, Enum):
    DEFAULT = "novel"
    NOVEL = "novel"
    ARTICLE = "article"
    COMIC = "comic"
    VIDEO = "video"

    @classmethod
    def values(cls):
        return list(dict.fromkeys(e.value for e in cls))
