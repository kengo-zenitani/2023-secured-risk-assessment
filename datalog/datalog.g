
elem comment: "#" comment./[^\n]*/ -> <Comment>{comment:as_str}</Comment>;

text predicate: /[_a-zA-Z][_a-zA-Z0-9]*/ -> {$$:as_str};

elem atom: /[a-z][_a-zA-Z0-9]*/ -> <Atom name={$$:as_str}/>;

elem variable: /[A-Z][_a-zA-Z0-9]*/ -> <Variable name={$$:as_str}/>;


elem fact: p.predicate "(" args.(atom ("," atom)+ | atom?) ")" -> <Fact predicate={p}>
    {*args:elem_only}
</Fact>;

elem term: p.predicate "(" args.((atom | variable) ("," (atom | variable))+ | (atom | variable)?) ")" -> <Term predicate={p}>
    {*args:elem_only}
</Term>;

elem rule: head.term ":-" body.(term ("," term)*) "." -> <Rule>
    <Head>{*head:elem_only}</Head>
    <Body>{*body:elem_only}</Body>
</Rule>;


elem aggregation: lhs./[a-z][_a-zA-Z0-9]*/ '=' '{' rhs.(atom (',' atom)*) '}' -> <Aggregate to={lhs}>
    {*rhs:elem_only}
</Aggregate>;


root: (rule | fact | aggregation | comment)* -> <Program>{*$$:elem_only}</Program>;

