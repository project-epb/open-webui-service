"""
title: (Filter) Hot fix for Deepseek-R1 reasoning_content block
version: 0.4.1
authors:
    - dragon-fish <dragon-fish@qq.com>
    - Deepseek-R1 <https://www.deepseek.com/>
url: https://github.com/project-epb/open-webui-service
description: |
    修复 Deepseek-R1 非标准 API 接口返回的推理内容块（reasoning_content）未能正确渲染的问题。
    Fix the problem that the reasoning content block (reasoning_content) returned by the non-standard API interface of Deepseek-R1 cannot be rendered correctly.

    ## 使用须知 / README

    本函数需要 open-webui >= 0.5.17
    因为使用了新的 "stream" 方法来处理事件流。
    安装后，勾选选择全局启用。开箱即用，没有额外的配置项。

    This function requires open-webui >= 0.5.17
    Because it uses the new "stream" method to process the event stream.
    After installation, check the global enable option. Ready to use, no additional configuration items.
"""


from typing import Dict


class Filter:
    # 初始化状态
    is_think_tag_open = False

    def __init__(self):
        pass

    def stream(self, event: Dict) -> Dict:
        try:
            if not (choices := event.get("choices")):
                return event

            last_choice = choices[-1]
            if not (delta := last_choice.get("delta")):
                return event

            # 预先提取可能的内容字段
            reasoning_content = delta.get("reasoning_content")
            normal_content = delta.get("content")

            # 优先处理正常内容（思考结束信号）
            if normal_content not in (None, ""):
                self._handle_normal_content(delta, normal_content)

            # 处理推理内容（思考过程）
            if reasoning_content not in (None, ""):
                self._handle_reasoning_content(delta, reasoning_content)

        except (IndexError, KeyError, TypeError) as e:
            # 生产环境建议添加日志记录
            # logger.error(f"Error processing event: {str(e)}")
            pass

        return event

    def _handle_reasoning_content(self, delta: Dict, content: str) -> None:
        """处理推理内容逻辑"""
        if not self.is_think_tag_open:
            delta["content"] = f"<think>{content}"
            self.is_think_tag_open = True
        else:
            delta["content"] = content

    def _handle_normal_content(self, delta: Dict, content: str) -> None:
        """处理普通内容逻辑"""
        if self.is_think_tag_open:
            delta["content"] = f"</think>{content}"
            self.is_think_tag_open = False
        else:
            delta["content"] = content
