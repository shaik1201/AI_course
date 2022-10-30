class Node:
    def __init__(self, value, next_node=None):

        self.value = value
        self.next = next_node

    def __str__(self):

        return str(self.value)


def sortedMerge(a, b): # This is the merging part like in normal merge sort.
    result = None

    # Base cases
    if a == None:
        return b
    if b == None:
        return a

    # pick either a or b and recur..
    if a.value <= b.value:
        result = a
        result.next = sortedMerge(a.next, b)
    else:
        result = b
        result.next = sortedMerge(a, b.next)
    return result

def getMiddle(head):
    if (head == None):
        return head

    slow = head
    fast = head

    while (fast.next != None and
            fast.next.next != None):
        slow = slow.next
        fast = fast.next.next
            
    return slow

def sort_in_place(head: Node) -> Node:
    if head == None or head.next == None:
        return head

    # get the middle of the list
    middle = getMiddle(head)
    nexttomiddle = middle.next

    # set the next of middle node to None
    middle.next = None

    # Apply mergeSort on left list
    left = sort_in_place(head)

    # Apply mergeSort on right list
    right = sort_in_place(nexttomiddle)

    # Merge the left and right lists
    sortedlist = sortedMerge(left, right)
    return sortedlist



if __name__ == '__main__':
    node1 = Node(1)
    node2 = Node(2, node1)
    node3 = Node(3, node2)

    tmp1 = node3

    while tmp1 is not None:
        print(tmp1.value)
        tmp1 = tmp1.next

    sort_in_place(node3)
    print('\n')

    tmp2 = node1

    while tmp2 is not None:
        print(tmp2.value)
        tmp2 = tmp2.next


print('feijb')