local function startswith(str, start)
    return string.sub(str, 1, string.len(start)) == start
end

local function hint(cand, input, reverse)
    -- 简码提示
    if utf8.len(cand.text) < 2 then
        return false
    end
    
    local lookup = " " .. reverse:lookup(cand.text) .. " "
    local short = string.match(lookup, " ([bcdefghjklmnpqrstwxyz;][aiouv]+) ") or 
                  string.match(lookup, " ([bcdefghjklmnpqrstwxyz;][bcdefghjklmnpqrstwxyz;]) ")
    if short and string.len(input) > 1 and not startswith(short, input) then
        cand:get_genuine().comment = cand.comment .. "〔" .. short .. "〕"
        return true
    end

    return false
end

local function commit_hint(cand, no_commit)
    -- 顶功提示
    cand:get_genuine().comment = '⛔'
end

local function filter(input, env)
    local context = env.engine.context
    local is_on = context:get_option('sbb_hint')
    local input_text = context.input
    local no_commit = string.len(input_text) < 4 and string.match(input_text, "^[bcdefghjklmnpqrstwxyz;]+$")
    for cand in input:iter() do
        if no_commit and cand.type == 'table' then
            commit_hint(cand, no_commit)
        end

        if is_on then
           hint(cand, input_text, env.reverse)
        end
        yield(cand)
    end
end

local function init(env)
    env.reverse = ReverseDb("build/xkjd27.extended.reverse.bin")
end

return { init = init, func = filter }