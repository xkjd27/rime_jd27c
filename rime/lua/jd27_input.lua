local conf = {
    number = {"〇", "一", "二", "三", "四", "五", "六", "七", "八", "九"},
    weekday = {"星期天", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"}
}

local function translateDateSuffix(text, type)
    for i = 1, string.len(text) do
        text = string.gsub(text, '〇', '', 1)
        if (type == 'day' and i == 1) then
            text = string.gsub(text, '^二', '二十', 1)
            text = string.gsub(text, '^三', '三十', 1)
        end
        if (type == 'month' or (type == 'day' and i == 2)) then
            text = string.gsub(text, '^一', '十', 1)
        end
    end
    return text
end

local function translateDate(text)
    local i = 0
    for key,value in ipairs(conf.number) do
        text = string.gsub(text, i, value)
        i = i + 1
    end
    return text
end

local function getUpDate()
    local h = os.date('%Y')
    local m = os.date('%m')
    local d = os.date('%d')

    local hour = translateDate(h)
    local month = translateDate(m)
    local month = translateDateSuffix(month, 'month')
    local day = translateDate(d)
    local day = translateDateSuffix(day, 'day')
    local res = string.format("%s年%s月%s日", hour, month, day)
    return res
end

local function getWeekDay()
    local week = os.date("%w")
    return conf.weekday[week + 1]
end

local function translator(input, seg, env)
    if input == env.date then
        yield(Candidate("jd27input", seg.start, seg._end, os.date("%Y年%m月%d日"), ""))
        yield(Candidate("jd27input", seg.start, seg._end, os.date("%Y-%m-%d"), ""))
        yield(Candidate("jd27input", seg.start, seg._end, getUpDate(), ""))
    elseif input == env.time then
        yield(Candidate("jd27input", seg.start, seg._end, os.date("%H:%M:%S"), ""))
    elseif input == env.week then
        yield(Candidate("jd27input", seg.start, seg._end, getWeekDay(), ""))
    end
end

local function init(env)
    local config = env.engine.schema.config

    env.date = config:get_string("input_code/date")
    env.time = config:get_string("input_code/time")
    env.week = config:get_string("input_code/week")
end

return { init = init, func = translator }