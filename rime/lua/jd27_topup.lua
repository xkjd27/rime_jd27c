--[[

    顶功处理器 by TsFreddie

    ------------
    Schema配置
    ------------
    1. 将topup.lua添加至rime.lua
        topup_processor = require("topup")
    
    2. 将topup_processor挂接在speller之前
        processors:
          ...
          - lua_processor@topup_processor
          - speller
          ...
    
    3. 配置顶功处理器
        topup:
            topup_with: "aeiov" # 顶功集合码，通常为形码
            min_length: 4  # 无顶功码自动上屏的长度
            max_length: 6  # 全码上屏的长度
            auto_clear: true  # 顶功空码时是否清空输入
]]

local function string2set(str)
    local t = {}
    for i = 1, #str do
        local c = str:sub(i,i)
        t[c] = true
    end
    return t
end

local function topup(env)
    if not env.engine.context:get_selected_candidate() then
        if env.auto_clear then
            env.engine.context:clear()
        else
            env.enabled = false
        end
    else
        env.engine.context:commit()
    end
end

local function processor(key_event, env)
    local engine = env.engine
    local schema = engine.schema
    local context = engine.context

    local input = context.input 
    local input_len = #input

    if key_event:release() or key_event:ctrl() or key_event:alt() then
        return 2
    end

    local ch = key_event.keycode

    if ch < 0x20 or ch >= 0x7f then
        return 2
    end

    local key = string.char(ch)

    local prev = string.sub(input, -1)

    local is_alphabet = env.alphabet[key] or false
    local is_topup = env.topup_set[key] or false
    local is_prev_topup = env.topup_set[prev] or false

    if not env.enabled then
        if context:get_selected_candidate() then
            env.enabled = true
        end
        return 2
    end

    if not is_alphabet then
        return 2
    end
    
    if is_prev_topup and not is_topup then
        topup(env)
    elseif not is_prev_topup and not is_topup and input_len >= env.topup_min then
        topup(env)
    elseif input_len >= env.topup_max then
        topup(env)
    end

    return 2
end

local function init(env)
    local config = env.engine.schema.config

    env.topup_set = string2set(config:get_string("topup/topup_with"))
    env.alphabet = string2set(config:get_string("speller/alphabet"))
    env.topup_min = config:get_int("topup/min_length")
    env.topup_max = config:get_int("topup/max_length")
    env.auto_clear = config:get_bool("topup/auto_clear")
    env.enabled = true
end

return { init = init, func = processor }