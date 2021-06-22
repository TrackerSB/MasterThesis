local VLIST = node.id("vlist")
local HLIST = node.id("hlist")
local GLUE = node.id("glue")
local RULE = node.id("rule")

magentabox = function(head)
    while head do
        if head.id == VLIST or head.id == HLIST then
            -- go through the hlists (the rows)
            magentabox(head.head)

            -- if there's a rule after the rightskip, this is the overfull box
            -- node id 10 == glue, glue subtype 9 is rightskip, node id 2 is a rule

        elseif head.id == GLUE and head.subtype == 9 and head.next and head.next.id == RULE then
            -- this must be an overfull box
            local w1, w2
            w1 = node.new("whatsit","pdf_literal")
            w1.data = "q 1 0.549 0 rg"
            w1.mode = 1
            w2 = node.new("whatsit","pdf_literal")
            w2.data = " Q"
            w2.mode = 1

            w1.next = head.next -- the rule
            head.next = w1      -- color start
            w1.next.next = w2   -- color end

            node.slide(head)    -- adjust prev pointers
        end
        head = head.next
    end
    return true
end
luatexbase.add_to_callback("post_linebreak_filter",magentabox,"magentabox")

