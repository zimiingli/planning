#!/bin/bash
###
 # @Author: zmli6 1281685748@qq.com
 # @Date: 2026-04-06 16:13:30
 # @LastEditors: zmli6 1281685748@qq.com
 # @LastEditTime: 2026-04-08 17:43:28
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

MAIN_REMOTE="origin"
OVERLEAF_REMOTE="overleaf"
BRANCH="main"
SUBTREE_PREFIX="writing"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${GREEN}[✓] $1${NC}"; }
warn()  { echo -e "${YELLOW}[!] $1${NC}"; }
error() { echo -e "${RED}[✗] $1${NC}"; exit 1; }

# 新增：提前提交本地改动，保证工作区干净
commit_local_changes() {
    if [ -n "$(git status --porcelain)" ]; then
        warn "检测到未提交的改动，正在提交..."
        git add .
        COMMIT_MSG="${1:-update $(date '+%Y-%m-%d %H:%M')}"
        git commit -m "$COMMIT_MSG"
    else
        info "工作区干净，无需提交"
    fi
}

do_pull() {
    echo ""
    echo "========== 拉取更新 =========="

    # 关键：subtree pull 要求工作区干净，先把本地改动提交掉
    commit_local_changes "$1"

    info "正在从 A 仓库 ($MAIN_REMOTE) 拉取..."
    # 用 merge 不用 rebase：rebase 会把 subtree --squash 产生的合并结构拆扁，
    # 导致下一次拉取时 squash commit 被当成普通 commit 重放，路径全部错位。
    git pull --no-rebase --no-edit $MAIN_REMOTE $BRANCH || error "从 A 仓库拉取失败"

    info "正在从 Overleaf ($OVERLEAF_REMOTE) 拉取 writing 更新..."
    if ! git subtree pull --prefix=$SUBTREE_PREFIX $OVERLEAF_REMOTE $BRANCH --squash -m "从 Overleaf 同步 writing 更新"; then
        # 检查是否处于冲突态，若有冲突中止整个流程，避免把冲突标记当成正常改动提交推送
        if [ -n "$(git ls-files -u)" ] || git status --porcelain | grep -qE '^(UU|AA|DD|AU|UA|DU|UD) '; then
            error "Overleaf 拉取产生合并冲突，请手动解决后再运行。可用 'git status' 查看冲突文件，解决后 'git add' 并 'git commit'，再重新执行本脚本。"
        else
            warn "Overleaf 拉取失败或无新更新（无冲突，继续）"
        fi
    fi

    info "拉取完成！"
}

do_push() {
    echo ""
    echo "========== 推送更新 =========="

    # 到这一步工作区应该已经干净了（do_sync 流程下），但单独 push 时也要兜底
    commit_local_changes "$1"

    info "正在推送到 A 仓库 ($MAIN_REMOTE)..."
    git push $MAIN_REMOTE $BRANCH || error "推送到 A 仓库失败"

    info "正在推送 writing 到 Overleaf ($OVERLEAF_REMOTE)..."
    git subtree push --prefix=$SUBTREE_PREFIX $OVERLEAF_REMOTE $BRANCH || warn "推送到 Overleaf 失败"

    info "推送完成！"
}

do_sync() {
    do_pull "$1"
    do_push "$1"
}

case "${1}" in
    pull)
        do_pull "$2"
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
        exit 1
        ;;
esac

echo ""
info "全部完成！"