"""
title: (Filter) Hot fix for Deepseek-R1 reasoning_content block
author: dragon-fish
author: Deepseek-R1
version: 0.4.0
"""

"""
使用须知
本函数需要 open-webui >= 0.5.17
因为使用了新的 "stream" 方法来处理事件流。
安装后，勾选选择全局启用。开箱即用，没有额外的配置项。
"""

"""
README
This function requires open-webui >= 0.5.17
Because it uses the new "stream" method to process the event stream.
After installation, check the global enable option. Ready to use, no additional configuration items.
"""


from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class Filter:
    def __init__(self):
        self.is_think_tag_open = False  # 状态

    def inlet(self, body: Dict) -> Dict:
        """Pass-through pre-processing hook"""
        return body

    def stream(self, event: Dict) -> Dict:
        """Stream processing hook with enhanced error handling"""
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

    def outlet(self, body: Dict) -> Dict:
        """Pass-through post-processing hook"""
        return body
