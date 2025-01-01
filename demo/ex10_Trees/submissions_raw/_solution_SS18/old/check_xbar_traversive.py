"""
Check whether a given tree conforms with X-bar theory.
Traversive version (traversal explicit).
"""


# ----------------------
# Properties of nodes
# ----------------------


def is_terminal(node):
    """Check whether a node is a terminal node (word).
    A node is terminal iff it has no children."""
    return len(node.children) == 0


def is_unary(node):
    """Check whether a node branches unary.
    A node branches unary iff it has 1 child."""
    return len(node.children) == 1


def is_binary(node):
    """Check whether a node branches binary.
    A node branches binary iff it has 2 children."""
    return len(node.children) == 2


def category(node):
    """Return the syntactic category of a node."""
    # Category of a node is given by chopping off the last character (projection level number) of its name.
    if not is_terminal(node):
        return node.name[0:len(node.name)-1]
    else:
        return category(node.parent)  # for terminal nodes, return category of parent (head)


def level(node):
    """Return the projection level of a node."""
    # Projection level of a node is given by extracting as an integer the last character (projection level) of its name.
    if not is_terminal(node):
        return int(node.name[len(node.name)-1])
    else:
        return level(node.parent)  # for terminal nodes, return proj. level of parent (head)


def same_cat(child, parent):
    """Check whether two nodes are of the same syntactic category."""
    return (parent is None or  # to prevent None error in case node to be checked is root
            category(child) == category(parent))


# ----------------------
# Check projection levels
# ----------------------

def traverse_is_xbar(tree):
    """Check by recursive traversal whether a tree conforms to X-bar structure."""
    return all(is_xbar(node) for node in tree.preorder())


def is_xbar(node):
    """A node conforms to X-bar structure iff it is a proper XP, X' or X."""
    return is_phrase(node) or is_bar(node) or is_head(node)


def is_phrase(node):
    """Check whether a node is a phrase (XP).
    A node is an XP iff it has projection level 2 and either
    - no specifier (unary branching into X') or
    - a specifier on the left (binary branching into a specifier YP and X')."""
    return (level(node) == 2 and
            (no_spec(node) or spec(node)))


def is_bar(node):
    """Check whether a node is a bar (X')
    A node is an X' iff it has projection level 1 of the same category as its XP and either
    - no adjuncts or complements (unary branching into the head X) or
    - a complement (binary branching into head X on the left and a complement YP on the right) or
    - an adjunct to the left or an adjunct to the right (binary branching into the adjunct YP and a second X' projection
    )."""
    return (level(node) == 1 and same_cat(node, node.parent) and
            (no_adj_or_compl(node) or compl(node) or adj(node)))


def is_head(node):
    """Check whether a node is a head (X).
    A node is an X iff it has projection level 0 of the same category as its X' and unary branches into a
    terminal node."""
    return (level(node) == 0 and same_cat(node, node.parent) and
            head(node))


# ----------------------
# Check structural constraints for the respective projection levels
# ----------------------


def no_spec(node):
    """XP structure with no specifier (unary branching into X')."""
    return (is_unary and
            level(node.children[0])) == 1 and same_cat(node.children[0], node)  # X'


def spec(node):
    """XP with specifier structure."""
    return (is_binary(node) and
            level(node.children[0]) == 2 and  # specifier YP on left
            level(node.children[1])) == 1 and same_cat(node.children[1], node)  # X' on right


def no_adj_or_compl(node):
    """X' structure with no complementation or adjunction; unary branching into head X."""
    return (is_unary(node) and
            level(node.children[0])) == 0 and same_cat(node.children[0], node)  # head X


def compl(node):
    """X' with head-complement structure."""
    return (is_binary(node) and
            level(node.children[0]) == 0 and same_cat(node.children[0]) and  # head X on left
            level(node.children[1])) == 2  # complement YP on right


def adj(node):
    """X' with adjunctive structure (adjunct on left or on right)."""
    return (is_binary(node) and
            ((level(node.children[0]) == 2 and  # adjunct YP on left
              level(node.children[1]) == 1 and same_cat(node.children[1], node))  # X' on right
             or
            (level(node.children[0]) == 1 and same_cat(node.children[0], node) and  # X' on left
             level(node.children[1]) == 2)))  # adjunct YP on right


def head(node):
    """X head branching unary into a terminal node (word)."""
    return (is_unary(node) and
            is_terminal(node.children[0]))  # terminal (word)
