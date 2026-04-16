## 转换模板

在开始审计前，请向 AI 发送以下指令：

> **指令：** 请根据我提供的文件名清单，按照以下规则输出 `rename_list.json`：
> 1. **核心格式：** `[国籍/朝代] 作者 - 书名: 副标题 (附加信息).扩展名`。
> 2. **作者修正：** 将 `姓, 名` 还原为 `名 姓`（如 `Figes, Orlando` 改为 `Orlando Figes`）。
> 3. **符号对齐：** 使用 ` - `（空格-横杠-空格）分隔作者与书名；使用冒号 `:` 分隔主副标题。
> 4. **去噪处理：** 彻底剔除 ISBN、哈希值、出版社、多余空格及“著/译/作品”等描述词。

---

## 示例

| 原始输入 (Anna's Archive 风格) | AI 审计输出 (JSON 右键值) |
| :--- | :--- |
| `(明)洪应明著 - 容斋随笔.pdf` | `[明] 洪应明 - 容斋随笔.pdf` |
| `Sajer, Guy -- The Forgotten Soldier -- 2a6a2...` | `[FR] Guy Sajer - The Forgotten Soldier.epub` |
| `Wiseguy_ life in a Mafia family -- Pileggi, Nicholas` | `[US] Nicholas Pileggi - Wiseguy: Life in a Mafia Family.epub` |
| `The Winter War _ The Soviet Attack -- Eloise Engle` | `[US] Eloise Engle - The Winter War: The Soviet Attack on Finland.epub` |

---

## 输出格式要求

AI 必须直接返回可供 `rename_from_list.py` 脚本读取的 **JSON 块**：

```json
{
  "原始文件名_噪音_ISBN.pdf": "[国籍] 作者 - 标准书名.pdf",
  "Old_Name_With_Hash.epub": "[代码] 作者 - 书名: 副标题.epub"
}
```

**执行逻辑：**
* 成功重命名的书籍将被物理隔离至源文件夹下的 `done/` 目录中。
* 脚本具备幂等性，若目标文件已存在则自动跳过。