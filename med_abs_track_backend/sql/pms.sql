-- 首先删除所有关联表
DROP TABLE IF EXISTS `pms_paper_author`;
DROP TABLE IF EXISTS `pms_paper_keyword`;
DROP TABLE IF EXISTS `pms_task_paper`;
DROP TABLE IF EXISTS `pms_user_paper`;

-- 然后删除依赖于其他表的主表
DROP TABLE IF EXISTS `pms_paper`;
DROP TABLE IF EXISTS `pms_extraction_task`;
DROP TABLE IF EXISTS `pms_extraction_method`;

-- 最后删除基础表（没有被其他表引用的表）
DROP TABLE IF EXISTS `pms_abstract_structure`;
DROP TABLE IF EXISTS `pms_author`;
DROP TABLE IF EXISTS `pms_journal`;
DROP TABLE IF EXISTS `pms_keyword`;
DROP TABLE IF EXISTS `pms_extraction_template`;
DROP TABLE IF EXISTS `pms_llm_model`;
DROP TABLE IF EXISTS `pms_prompt_template`;
-- ----------------------------
-- Table structure for pms_abstract_structure
-- ----------------------------
CREATE TABLE `pms_abstract_structure` (
  `abstract_id` int NOT NULL AUTO_INCREMENT COMMENT '摘要结构ID',
  `background` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '背景部分文本',
  `methods` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '方法部分文本',
  `results` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '结果部分文本',
  `conclusion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '结论部分文本',
  `content` json DEFAULT NULL COMMENT '结构化内容（JSON格式）',
  `extraction_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '抽取日期时间',
  `status` char(1) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '0' COMMENT '状态（0正常 1异常）',
  `is_extracted` tinyint(1) NOT NULL DEFAULT '1' COMMENT '是否成功抽取',
  `create_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`abstract_id`),
  KEY `idx_is_extracted` (`is_extracted`),
  KEY `idx_status` (`status`),
  FULLTEXT KEY `ft_all_content` (`background`,`methods`,`results`,`conclusion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='摘要结构化抽取结果表';

-- ----------------------------
-- Table structure for pms_author
-- ----------------------------
CREATE TABLE `pms_author` (
  `author_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '作者姓名',
  `affiliation` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '作者所属机构',
  `create_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`author_id`),
  KEY `idx_author_name` (`name`(50)),
  KEY `idx_name_affiliation` (`name`(50),`affiliation`(50))
) ENGINE=InnoDB AUTO_INCREMENT=170 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='论文作者表';

-- ----------------------------
-- Table structure for pms_extraction_method
-- ----------------------------
CREATE TABLE `pms_extraction_method` (
  `method_id` int NOT NULL AUTO_INCREMENT,
  `method_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '抽取方法名称',
  `method_type` enum('regex','llm','rule','ml','other') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '抽取方法类型: regex, llm, rule, ml或其他未来方法',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '方法描述',
  `config_params` json DEFAULT NULL COMMENT '配置参数（JSON格式）',
  `template_id` int DEFAULT NULL COMMENT '抽取模板ID，用于regex/rule方法',
  `model_id` int DEFAULT NULL COMMENT '大语言模型ID，用于llm方法',
  `prompt_id` int DEFAULT NULL COMMENT 'Prompt模板ID，用于llm方法',
  `status` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
  `create_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`method_id`),
  UNIQUE KEY `idx_method_name` (`method_name`),
  KEY `idx_method_type` (`method_type`),
  KEY `idx_status` (`status`),
  KEY `idx_template_id` (`template_id`),
  KEY `idx_model_id` (`model_id`),
  KEY `idx_prompt_id` (`prompt_id`),
  CONSTRAINT `fk_method_model` FOREIGN KEY (`model_id`) REFERENCES `pms_llm_model` (`model_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_method_prompt` FOREIGN KEY (`prompt_id`) REFERENCES `pms_prompt_template` (`prompt_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_method_template` FOREIGN KEY (`template_id`) REFERENCES `pms_extraction_template` (`template_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='抽取方法配置表';

-- ----------------------------
-- Table structure for pms_extraction_task
-- ----------------------------
CREATE TABLE `pms_extraction_task` (
  `task_id` int NOT NULL AUTO_INCREMENT,
  `method_id` int NOT NULL COMMENT '抽取方法ID',
  `execution_parameters` json DEFAULT NULL COMMENT '执行参数',
  `status` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '0' COMMENT '状态（0待处理 1处理中 2已完成 3失败）',
  `started_at` datetime DEFAULT NULL COMMENT '开始时间',
  `completed_at` datetime DEFAULT NULL COMMENT '完成时间',
  `error_message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '错误信息',
  `create_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`task_id`),
  KEY `idx_status` (`status`),
  KEY `idx_method_id` (`method_id`),
  CONSTRAINT `fk_task_method` FOREIGN KEY (`method_id`) REFERENCES `pms_extraction_method` (`method_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='摘要抽取任务表';

-- ----------------------------
-- Table structure for pms_extraction_template
-- ----------------------------
CREATE TABLE `pms_extraction_template` (
  `template_id` int NOT NULL AUTO_INCREMENT,
  `template_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '模板名称',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '模板描述',
  `template_content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '模板内容/规则',
  `status` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
  `create_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`template_id`),
  UNIQUE KEY `idx_template_name` (`template_name`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='摘要抽取模板表';

-- ----------------------------
-- Table structure for pms_journal
-- ----------------------------
CREATE TABLE `pms_journal` (
  `journal_id` int NOT NULL AUTO_INCREMENT,
  `journal_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '期刊名称',
  `country` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '期刊所属国家',
  `issn` varchar(9) CHARACTER SET ascii COLLATE ascii_general_ci DEFAULT NULL COMMENT '期刊ISSN号',
  `create_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`journal_id`),
  UNIQUE KEY `idx_journal_name` (`journal_name`),
  KEY `idx_issn` (`issn`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='期刊信息表';

-- ----------------------------
-- Table structure for pms_keyword
-- ----------------------------
CREATE TABLE `pms_keyword` (
  `keyword_id` int NOT NULL AUTO_INCREMENT,
  `keyword` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '关键词文本',
  `create_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`keyword_id`),
  KEY `idx_keyword` (`keyword`(50))
) ENGINE=InnoDB AUTO_INCREMENT=157 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='论文关键词表';

-- ----------------------------
-- Table structure for pms_llm_model
-- ----------------------------
CREATE TABLE `pms_llm_model` (
  `model_id` int NOT NULL AUTO_INCREMENT,
  `display_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '显示名称（用户友好的描述性名称）',
  `model_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'OpenAI模型名称（如gpt-4, gpt-3.5-turbo等）',
  `model_version` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '模型版本（如0613, 0125-preview等）',
  `provider` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'OpenAI' COMMENT '模型提供商',
  `base_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'https://api.openai.com/v1' COMMENT 'API基础URL',
  `api_key` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'OpenAI API密钥（加密存储）',
  `organization_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'OpenAI组织ID',
  `default_parameters` json DEFAULT NULL COMMENT '默认参数配置（temperature, max_tokens等）',
  `context_length` int DEFAULT NULL COMMENT '模型上下文长度限制',
  `request_timeout` int DEFAULT '30' COMMENT '请求超时时间（秒）',
  `status` char(1) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
  `create_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`model_id`),
  UNIQUE KEY `idx_display_name` (`display_name`),
  UNIQUE KEY `idx_model_name_version` (`model_name`,`model_version`),
  KEY `idx_status` (`status`),
  KEY `idx_provider` (`provider`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='大语言模型配置表';

-- ----------------------------
-- Table structure for pms_paper
-- ----------------------------
CREATE TABLE `pms_paper` (
  `paper_id` int NOT NULL AUTO_INCREMENT,
  `pmid` varchar(20) CHARACTER SET ascii COLLATE ascii_general_ci DEFAULT NULL COMMENT 'PubMed ID',
  `doi` varchar(100) CHARACTER SET ascii COLLATE ascii_general_ci DEFAULT NULL COMMENT '数字对象标识符',
  `title` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '论文标题',
  `abstract` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '论文摘要',
  `abstract_id` int DEFAULT NULL COMMENT '摘要结构ID',
  `journal_id` int DEFAULT NULL COMMENT '期刊ID',
  `status` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '0' COMMENT '状态（0预发表 1已出版）',
  `received_date` date DEFAULT NULL COMMENT '收稿日期',
  `accepted_date` date DEFAULT NULL COMMENT '接受日期',
  `published_date` date DEFAULT NULL COMMENT '发表日期',
  `create_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`paper_id`),
  UNIQUE KEY `pmid` (`pmid`),
  UNIQUE KEY `doi` (`doi`),
  KEY `idx_published_date` (`published_date`),
  KEY `idx_status` (`status`),
  KEY `idx_journal_id` (`journal_id`),
  KEY `idx_abstract_id` (`abstract_id`),
  FULLTEXT KEY `ft_title_abstract` (`title`,`abstract`),
  CONSTRAINT `fk_paper_abstract` FOREIGN KEY (`abstract_id`) REFERENCES `pms_abstract_structure` (`abstract_id`),
  CONSTRAINT `fk_paper_journal` FOREIGN KEY (`journal_id`) REFERENCES `pms_journal` (`journal_id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='围手术期相关论文信息表';

-- ----------------------------
-- Table structure for pms_paper_author
-- ----------------------------
CREATE TABLE `pms_paper_author` (
  `paper_id` int NOT NULL COMMENT '论文ID',
  `author_id` int NOT NULL COMMENT '作者ID',
  `author_order` int NOT NULL COMMENT '作者排序',
  PRIMARY KEY (`paper_id`,`author_id`),
  KEY `idx_paper_author` (`paper_id`,`author_id`,`author_order`),
  KEY `idx_author_paper` (`author_id`,`paper_id`),
  CONSTRAINT `fk_paper_author_author_id` FOREIGN KEY (`author_id`) REFERENCES `pms_author` (`author_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_paper_author_paper_id` FOREIGN KEY (`paper_id`) REFERENCES `pms_paper` (`paper_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='论文与作者关联表';

-- ----------------------------
-- Table structure for pms_paper_keyword
-- ----------------------------
CREATE TABLE `pms_paper_keyword` (
  `paper_id` int NOT NULL COMMENT '论文ID',
  `keyword_id` int NOT NULL COMMENT '关键词ID',
  PRIMARY KEY (`paper_id`,`keyword_id`),
  KEY `idx_paper_keyword` (`paper_id`,`keyword_id`),
  KEY `idx_keyword_paper` (`keyword_id`,`paper_id`),
  CONSTRAINT `fk_paper_keyword_keyword_id` FOREIGN KEY (`keyword_id`) REFERENCES `pms_keyword` (`keyword_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_paper_keyword_paper_id` FOREIGN KEY (`paper_id`) REFERENCES `pms_paper` (`paper_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='论文与关键词关联表';

-- ----------------------------
-- Table structure for pms_prompt_template
-- ----------------------------
CREATE TABLE `pms_prompt_template` (
  `prompt_id` int NOT NULL AUTO_INCREMENT,
  `prompt_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Prompt名称',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT 'Prompt描述',
  `prompt_content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Prompt内容',
  `status` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
  `create_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`prompt_id`),
  UNIQUE KEY `idx_prompt_name` (`prompt_name`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Prompt模板表';

-- ----------------------------
-- Table structure for pms_task_paper
-- ----------------------------
CREATE TABLE `pms_task_paper` (
  `task_id` int NOT NULL COMMENT '任务ID',
  `paper_id` int NOT NULL COMMENT '论文ID',
  PRIMARY KEY (`task_id`,`paper_id`),
  KEY `idx_task_paper` (`task_id`,`paper_id`),
  KEY `idx_paper_task` (`paper_id`,`task_id`),
  CONSTRAINT `fk_task_paper_paper_id` FOREIGN KEY (`paper_id`) REFERENCES `pms_paper` (`paper_id`),
  CONSTRAINT `fk_task_paper_task_id` FOREIGN KEY (`task_id`) REFERENCES `pms_extraction_task` (`task_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='抽取任务与论文关联表';

-- ----------------------------
-- Table structure for pms_user_paper
-- ----------------------------
CREATE TABLE `pms_user_paper` (
  `user_id` int NOT NULL COMMENT '用户ID',
  `paper_id` int NOT NULL COMMENT '论文ID',
  PRIMARY KEY (`user_id`,`paper_id`) USING BTREE,
  KEY `fk_user_paper_paper_id` (`paper_id`),
  CONSTRAINT `fk_user_paper_paper_id` FOREIGN KEY (`paper_id`) REFERENCES `pms_paper` (`paper_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户和论文关联表';