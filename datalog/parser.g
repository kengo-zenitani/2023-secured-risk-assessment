
attr abstract_spec:
	"abstract" -> [abstract="true"];
	empty -> [abstract="false"];

attr scope_spec:
	"public" -> [scope="public"];
	"protected" -> [scope="protected"];
	"private" -> [scope="true"];
	empty -> [];

elem class_def:
	abstract_spec scope_spec "class" name.signature ... -> <Class name={name} {abstract_spec} {scope_spec}>...</Class>;


elem if_stmt:

    "if" cond.formula# ":"# then.block^ elif.("elif"= cond.formula ":" action.block^)+ "else:"= else.block^ -> <If>
        <Cond>{cond}</Cond>
        <Then>{then}</Then>
        {elif:case => <Elif>
            <Cond>{case.cond}</Cond>
            <Then>{case.action}</Then>
        </Elif>}
        <Else>{else}</Else>
    </If>;

    "if" cond.formula# ":"# then.block^ "else:"= else.block^ -> <If>
        <Cond>{cond}</Cond>
        <Then>{then}</Then>
        <Else>{else}</Else>
    </If>;

    "if" cond.formula# ":"# then.block^ -> <If>
        <Cond>{cond}</Cond>
        <Then>{then}</Then>
    </If>;


elem add: "+" -> <Add/>;
elem sub: "-" -> <Sub/>;

elem mul: "*" -> <Mul/>;
elem div: "/" -> <Div/>;


elem formula: element ((add|sub) element)* -> {$$:foldl};
elem element: factor ((mul|div) factor)* -> {$$:foldr};

elem factor:
    '(' val.formula ')' -> {val};
    numeric -> <Number>{$1}</Number>;

text numeric:
    [0-9]+  -> {$1};
    "+" numeric  -> {$2};
    "-" numeric  -> {$1}{$2};
