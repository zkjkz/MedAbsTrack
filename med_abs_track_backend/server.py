from contextlib import asynccontextmanager
from fastapi import FastAPI
from config.env import AppConfig
from config.get_db import init_create_table
from config.get_redis import RedisUtil
from config.get_scheduler import SchedulerUtil
from exceptions.handle import handle_exception
from middlewares.handle import handle_middleware
from module_admin.controller.cache_controller import cacheController
from module_admin.controller.captcha_controller import captchaController
from module_admin.controller.common_controller import commonController
from module_admin.controller.config_controller import configController
from module_admin.controller.dept_controller import deptController
from module_admin.controller.dict_controller import dictController
from module_admin.controller.log_controller import logController
from module_admin.controller.login_controller import loginController
from module_admin.controller.job_controller import jobController
from module_admin.controller.menu_controller import menuController
from module_admin.controller.notice_controller import noticeController
from module_admin.controller.online_controller import onlineController
from module_admin.controller.post_controler import postController
from module_admin.controller.role_controller import roleController
from module_admin.controller.server_controller import serverController
from module_admin.controller.user_controller import userController
from module_generator.controller.gen_controller import genController
from sub_applications.handle import handle_sub_applications
from utils.log_util import logger
from module_literature.controller.extraction_template_controller import (
    extraction_templateController,
)
from module_literature.controller.prompt_template_controller import (
    prompt_templateController,
)
from module_literature.controller.paper_controller import paperController
from module_literature.controller.llm_model_controller import llm_modelController
from module_literature.controller.extraction_method_controller import (
    extraction_methodController,
)
from module_literature.controller.extraction_task_controller import (
    extractionTaskController,
)
from module_literature.controller.abstract_structure_controller import (
    abstractStructureController,
)
from module_literature.controller.paper_search_controller import paperSearchController
from module_literature.controller.statistics_controller import statisticsController
from module_literature.controller.author_controller import authorController
from module_literature.controller.journal_controller import journalController
from module_literature.controller.keyword_controller import keywordController
from module_literature.service.extractor import init_extractors


# 生命周期事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"{AppConfig.app_name}开始启动")
    await init_create_table()
    app.state.redis = await RedisUtil.create_redis_pool()
    await RedisUtil.init_sys_dict(app.state.redis)
    await RedisUtil.init_sys_config(app.state.redis)
    await SchedulerUtil.init_system_scheduler()
    # 初始化抽取器
    init_extractors()
    logger.info("初始化抽取器成功")
    logger.info(f"{AppConfig.app_name}启动成功")
    yield
    await RedisUtil.close_redis_pool(app)
    await SchedulerUtil.close_system_scheduler()


# 初始化FastAPI对象
app = FastAPI(
    title=AppConfig.app_name,
    description=f"{AppConfig.app_name}接口文档",
    version=AppConfig.app_version,
    lifespan=lifespan,
)

# 挂载子应用
handle_sub_applications(app)
# 加载中间件处理方法
handle_middleware(app)
# 加载全局异常处理方法
handle_exception(app)


# 加载路由列表
controller_list = [
    {"router": loginController, "tags": ["登录模块"]},
    {"router": captchaController, "tags": ["验证码模块"]},
    {"router": paperController, "tags": ["文献管理-文献"]},
    {"router": paperSearchController, "tags": ["文献管理-文献搜索"]},
    {"router": extraction_methodController, "tags": ["文献管理-抽取方法"]},
    {"router": abstractStructureController, "tags": ["文献管理-摘要结构"]},
    {"router": extraction_templateController, "tags": ["文献管理-抽取模板"]},
    {"router": prompt_templateController, "tags": ["文献管理-提示模板"]},
    {"router": llm_modelController, "tags": ["文献管理-大语言模型"]},
    {"router": extractionTaskController, "tags": ["文献管理-抽取任务"]},
    {"router": statisticsController, "tags": ["文献管理-统计分析"]},
    {"router": authorController, "tags": ["文献管理-作者"]},
    {"router": journalController, "tags": ["文献管理-期刊"]},
    {"router": keywordController, "tags": ["文献管理-关键词"]},
    {"router": userController, "tags": ["系统管理-用户管理"]},
    {"router": roleController, "tags": ["系统管理-角色管理"]},
    {"router": menuController, "tags": ["系统管理-菜单管理"]},
    {"router": deptController, "tags": ["系统管理-部门管理"]},
    {"router": postController, "tags": ["系统管理-岗位管理"]},
    {"router": dictController, "tags": ["系统管理-字典管理"]},
    {"router": configController, "tags": ["系统管理-参数管理"]},
    {"router": noticeController, "tags": ["系统管理-通知公告管理"]},
    {"router": logController, "tags": ["系统管理-日志管理"]},
    {"router": onlineController, "tags": ["系统监控-在线用户"]},
    {"router": jobController, "tags": ["系统监控-定时任务"]},
    {"router": serverController, "tags": ["系统监控-菜单管理"]},
    {"router": cacheController, "tags": ["系统监控-缓存监控"]},
    {"router": commonController, "tags": ["通用模块"]},
    {"router": genController, "tags": ["代码生成"]},
]

for controller in controller_list:
    app.include_router(router=controller.get("router"), tags=controller.get("tags"))
