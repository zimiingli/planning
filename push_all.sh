#!/bin/bash
###
 # @Author: zmli6 1281685748@qq.com
 # @Date: 2026-04-06 16:13:30
 # @LastEditors: zmli6 1281685748@qq.com
 # @LastEditTime: 2026-04-06 16:18:46
 # @FilePath: /undefined/Users/liziming/Desktop/project/text_planning/research_analysis/push_all.sh
 # @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
### 

# ============================================
# Git 同步脚本 - A仓库 & Overleaf(B仓库) 同步
# 用法:
#   ./sync.sh pull    - 拉取两边的更新
#   ./sync.sh push    - 推送到两边
#   ./sync.sh sync    - 先拉取再推送（完整同步）
#   ./sync.sh         - 默认执行 sync
# ============================================

# 配置
MAIN_REMOTE="origin"
OVERLEAF_REMOTE="overleaf"
BRANCH="main"
SUBTREE_PREFIX="writing"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

info()  { echo -e "${GREEN}[✓] $1${NC}"; }
warn()  { echo -e "${YELLOW}[!] $1${NC}"; }
error() { echo -e "${RED}[✗] $1${NC}"; exit 1; }

do_pull() {
    echo ""
    echo "========== 拉取更新 =========="

    # 1. 拉取 A 仓库
    info "正在从 A 仓库 ($MAIN_REMOTE) 拉取..."
    git pull $MAIN_REMOTE $BRANCH || error "从 A 仓库拉取失败"

    # 2. 拉取 Overleaf (B 仓库) 的改动到 writing 文件夹
    info "正在从 Overleaf ($OVERLEAF_REMOTE) 拉取 writing 更新..."
    git subtree pull --prefix=$SUBTREE_PREFIX $OVERLEAF_REMOTE $BRANCH --squash -m "从 Overleaf 同步 writing 更新" || warn "Overleaf 拉取失败或无新更新"

    info "拉取完成！"
}

do_push() {
    echo ""
    echo "========== 推送更新 =========="

    # 1. 检查是否有未提交的改动
    if [ -n "$(git status --porcelain)" ]; then
        warn "检测到未提交的改动，正在提交..."
        git add .
        COMMIT_MSG="${1:-update $(date '+%Y-%m-%d %H:%M')}"
        git commit -m "$COMMIT_MSG"
    else
        info "没有未提交的改动"
    fi

    # 2. 推送到 A 仓库
    info "正在推送到 A 仓库 ($MAIN_REMOTE)..."
    git push $MAIN_REMOTE $BRANCH || error "推送到 A 仓库失败"

    # 3. 推送 writing 到 Overleaf (B 仓库)
    info "正在推送 writing 到 Overleaf ($OVERLEAF_REMOTE)..."
    git subtree push --prefix=$SUBTREE_PREFIX $OVERLEAF_REMOTE $BRANCH || warn "推送到 Overleaf 失败"

    info "推送完成！"
}

do_sync() {
    do_pull
    do_push "$1"
}

# 主逻辑
case "${1}" in
    pull)
        do_pull
        ;;
    push)
        do_push "$2"
        ;;
    sync|"")
        do_sync "$2"
        ;;
    *)
        echo "用法: $0 {pull|push|sync} [提交信息]"
        echo ""
        echo "  pull  - 从 A 仓库和 Overleaf 拉取更新"
        echo "  push  - 提交并推送到 A 仓库和 Overleaf"
        echo "  sync  - 先拉取再推送（默认）"
        echo ""
        echo "示例:"
        echo "  $0 pull"
        echo "  $0 push \"修改了论文第三章\""
        echo "  $0 sync"
        exit 1
        ;;
esac

echo ""
info "全部完成！"