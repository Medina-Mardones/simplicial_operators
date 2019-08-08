#!/usr/bin/env python
# coding: utf-8

# In[1]:


from itertools import combinations, product, chain, permutations

def partitions(n,k,l=1):
    '''n is the integer to partition and k is the length of partitions
    we get all k tuples in non-decreassing order of positive integers
    adding to n'''
    if k == 1:
        if n >= l:
            yield (n,)
        return
    for i in range(l,n+1):
        for result in partitions(n-i,k-1,i):
            yield (i,)+result
            
####### OPERATOR - BIOPERATOR #########

class Operator(object):
    '''
    Models a simplicial operator of the form:

    s ... s d ... d

    represented in the canonical form

    s > ... > s d < ... < d

    Parameters
    ----------
    deg_maps  : tuple or list
                An ordered collection of integers representing the degeneracy maps of the operator

    face_maps : tuple or list
                An ordered collection of integers representing the face maps of the operator

    '''

    def __init__(self, deg_maps = [], face_maps = []):

        self.deg_maps  = Operator.deg_maps_sort(deg_maps)
        self.face_maps = Operator.face_maps_sort(face_maps)

    def __repr__(self):

        s, d = repr(self.deg_maps), repr(self.face_maps)

        return f'Operator(deg_maps={s}, face_maps={d})'

    def __str__(self):

        if not self.deg_maps and not self.face_maps:

            return 'id'

        if not self.deg_maps:
            s = ''
        else:
            s = f's_{"s_".join(str(i) for i in self.deg_maps)}'

        if not self.face_maps:
            d = ''
        else:
            d = f'd_{"d_".join(str(i) for i in self.face_maps)}'

        return(s+d)

    def __call__(self, simplex):
        '''applies the operator to a simplex represented by a list or a tuple'''

        simplex = list(simplex)

        if self.face_maps and len(simplex)-1 < self.face_maps[-1]:
            raise ValueError('simplex not in the domain of the operator')

        # face maps
        simplex = ([v for i, v in enumerate(simplex)
                    if i not in self.face_maps])

        # degeneracy maps
        for i in sorted(self.deg_maps):
            try:
                simplex.insert(i+1, simplex[i])
            except IndexError:
                raise ValueError('simplex not in the domain of the operator')

        return tuple(simplex)

    @property
    def degree(self):
        '''returns the degree of the operator as an int'''

        return len(self.deg_maps) - len(self.face_maps)

    @property
    def is_degenerate(self):
        '''returns True if the operator is degenerate and False if not'''

        return bool(self.deg_maps)

    def compose(self, other):
        '''returns the operator self other'''

        s_left, d_left  = list(self.deg_maps), list(self.face_maps)
        s_right, d_right = list(other.deg_maps), list(other.face_maps)

        # getting s_right passed d_left
        d = d_left
        s = []
        for j in s_right:
            if j+1 in d or j in d:
                p = max(filter(lambda k: k == j or k == j+1, d))
                d = d[:d.index(p)] + [k-1 for k in d[d.index(p)+1:]]

            else:
                lt = list(filter(lambda k: k < j, d))
                gt = list(filter(lambda k: k > j+1, d))
                d = lt + [k-1 for k in gt]
                s.append(j - len(lt))

        # One can maybe optimize the following using that
        # s_left, s, d, and d_right are totally ordered

        new_deg_maps  = Operator.deg_maps_sort(s_left + s)
        new_face_maps = Operator.face_maps_sort(d + d_right)

        return Operator(new_deg_maps, new_face_maps)

    def prime(self):
        '''adds 1 to all the numbers defining the face and degeneracy maps 
        of the operator'''
        
        return Operator((v+1 for v in self.deg_maps),
                        (w+1 for w in self.face_maps))
    
    @staticmethod
    def deg_maps_sort(deg_maps):
        '''puts the degeneracy maps in canonical order s > ... > s using
        the simplicial identity s_i s_j = s_{j+1} s_i if i <= j'''

        deg_maps = list(deg_maps)
        for index in reversed(range(len(deg_maps)-1)):

            currentvalue = deg_maps[index]
            position = index

            while (position<len(deg_maps)-1 and
                   currentvalue <= deg_maps[position+1]):

                deg_maps[position] = deg_maps[position+1]+1
                position = position+1

            deg_maps[position] = currentvalue

        return tuple(deg_maps)

    @staticmethod
    def face_maps_sort(face_maps):
        '''puts the face maps in canonical order d < ... < d using the
        simplicial identity d_i d_j = d_j d_{i+1} if i >= j'''

        face_maps = list(face_maps)
        for index in range(1, len(face_maps)):

            currentvalue = face_maps[index]
            position = index

            while (position > 0 and
                   face_maps[position-1] >= currentvalue):

                face_maps[position] = face_maps[position-1]+1
                position = position-1

            face_maps[position] = currentvalue

        return tuple(face_maps)
    

class Bioperator:
    '''
    Models a simplicial bioperator of form:

    s ... s d ... d (x) s ... s d ... d

    represented in the canonical form

    s > ... > s d < ... < d (x) s > ... > s d < ... < d
    '''

    def __init__(self, deg_maps1=[], face_maps1=[], 
                       deg_maps2=[], face_maps2=[]):
        
        if isinstance(deg_maps1, Operator) and isinstance(face_maps1, Operator):
            self.op1 = deg_maps1
            self.op2 = face_maps1
        else:
            self.op1 = Operator(deg_maps1, face_maps1)
            self.op2 = Operator(deg_maps2, face_maps2)

    def __repr__(self):

        s1, d1 = self.op1.deg_maps, self.op1.face_maps
        s2, d2 = self.op2.deg_maps, self.op2.face_maps

        return (f'Bioperator(deg_maps1={s1}, face_maps1={d1}, '
                         + f'deg_maps2={s2}, face_maps2={d2})')

    def __str__(self):

        return(str(self.op1) + ' x ' + str(self.op2))

    def __call__(self, spx1, spx2=None):
        
        if spx2 is None:
            return self.op1(spx1), self.op2(spx1)
        else:
            return self.op1(spx1), self.op2(spx2)
    
    @property
    def bidegree(self):
        '''returns the bidegree of the operator as a pair of int'''

        return self.op1.degree(), self.op2.degree()
    
    @property
    def is_degenerate(self):
        '''returns True if the operator is degenerate and False if not'''

        s1 = set(self.op1.deg_maps)
        s2 = set(self.op2.deg_maps)

        return bool(s1.intersection(s2))

    def compose(self, other):
        '''returns the operator self other'''

        op1 = self.op1.compose(other.op1)
        op2 = self.op2.compose(other.op2)

        return Bioperator(op1.deg_maps, op1.face_maps,
                          op2.deg_maps, op2.face_maps)
    
    def prime(self):
        '''adds 1 to all the numbers defining the face and degeneracy maps 
        of the operator'''
        
        return Bioperator(self.op1.prime(), self.op2.prime())

####### EZ-AW #########

def alexander_whitney(n, q=None):
    '''if an integer n is passed it returns the linear combination of bioperators defining the 
    restriction of AW to degree n. If two integers (p, q) are passed it provides the single 
    bioperad defining the projection to bidegree (p, q) of the AW map'''
    
    if not q is None:
        p = n
        return Bioperator(face_maps1 = range(p+1,p+q+1), 
                          face_maps2 = range(0,p))
    
    # dictionary of bioperators indexed by (-n,0), (-n+1, -1), ... , (0,-n)
    if q == None:
        answer = {}
        for i in range(n+1):
            answer[(-n+i, -i)] = Bioperator(face_maps1 = range(i+1,n+1), 
                                            face_maps2 = range(0,i))

        return answer
    
def eilenberg_zilber(n, q=None, all_bidegrees=False):
    '''if a single integer n is passed, it returns a dictionary whose keys are bidegrees adding to n
    and values the bioperators defining the restriction of EZ to that bidegree. If all_bidegrees 
    is True it gives the same but the condition is that bidegrees add up to less than or equal to n.
    
    If a pair of integers p,q is passed it returns the bioperators defining EZ in bidegree (p,q). 
    If all_bidegrees is true it acts as if a single integer p+q was passed.'''
    
    # operators in bidegree (q,p) acting on elements of bidegree (p,q)
    if q != None:
        p = n
        if (p,q) == (0,0):
            return {Bioperator()}

        answer = set()
        if p > 0:
            west = eilenberg_zilber(p-1, q)
            for biop in west:
                answer ^= {Bioperator(
                                deg_maps1 = biop.op1.deg_maps,
                                deg_maps2 = [p+q-1] + list(biop.op2.deg_maps))}
        if q > 0:
            south = eilenberg_zilber(p, q-1)
            for biop in south:
                answer ^= {Bioperator(
                                deg_maps1 = [p+q-1] + list(biop.op1.deg_maps),
                                deg_maps2 = biop.op2.deg_maps)}
        return answer
    
    # dictionary of all bioperators indexed by bidegrees
    # (memory intensive)
    if all_bidegrees:
        if q:
            n += q
            
        answer = {(0,0): {Bioperator()}}
        for m in range(1, n+1):
            answer.update({(p,m-p): set() for p in range(m+1)})
            for i in range(m):
                j = m-i-1
                for biop in answer[(i,j)]:
                    answer[(i,j+1)] ^= {Bioperator(
                                            deg_maps1 = biop.op1.deg_maps,
                                            deg_maps2 = [i+j] + list(biop.op2.deg_maps))}

                    answer[(i+1,j)] ^= {Bioperator(
                                            deg_maps1 = [i+j] + list(biop.op1.deg_maps),
                                            deg_maps2 = biop.op2.deg_maps)}
            
        return answer
    
    # dictionary of bioperators indexed by bidegrees (0,n), (1,n-1), ... , (n,0)
    if q == None:
        if n == 0:
            return {(0,0) : {Bioperator()}}

        if n > 0:
            answer = {(i,n-i): set() for i in range(n+1)}
            for bidegree, biops in eilenberg_zilber(n-1).items():
                i, j = bidegree
                answer[(i,j+1)] ^= {Bioperator(
                                        deg_maps1 = biop.op1.deg_maps,
                                        deg_maps2 = [i+j] + list(biop.op2.deg_maps))
                                            for biop in biops}

                answer[(i+1,j)] ^= {Bioperator(
                                        deg_maps1 = [i+j] + list(biop.op1.deg_maps),
                                        deg_maps2 = biop.op2.deg_maps)
                                            for biop in biops}
            return answer

def shih(n):
    '''returns all bioperators defining the chain homotopy between 
    EZAW and the identity. Some of them are degenerate.'''
    
    if n == 0:
        return set()
    
    s_0s_0 = Bioperator(deg_maps1=[0], deg_maps2=[0])
    
    ez = eilenberg_zilber(n)
    aw = alexander_whitney(n)
    ezaw = set()
    for i in range(n+1):
        ezaw ^= {biop.compose(aw[(-i,-n+i)]) for biop in ez[(i,n-i)]}
        
    answer = {biop.prime().compose(s_0s_0) for biop in ezaw}
    
    if n == 1:
        return answer

    if n > 1:
        return answer^{biop.prime() for biop in shih(n-1)}
        
######## STEENROD ########

def steenrod_diagonal(n,i):
    '''...'''
    if type(n) != int or n < 0 :
        raise ValueError('The first entry (dimension) must be a non-negative integer')
    
    elif type(i) != int :
        raise ValueError('The second entry (i) must be an integer')

    elif n < i or i < 0 :
        return set() # no operators model for 0 operator
    
    answer = set()
    for U in combinations(range(n+1), n-i):
        
        U_minus, U_plus = [], []
        for u in U :
            if (U.index(u) + u) % 2 == 1:
                U_minus.append(u)
            else :
                U_plus.append(u)
        
        answer ^= {Bioperator(face_maps1 = U_minus, 
                              face_maps2 = U_plus)}
    
    return answer

######### TABLE REDUCTION ###########
def table_reduction(bar_ecc_elements):
    '''given a set of basis element in the Barratt-Eccles operad, it returns the set of
        surjections in its image via the table reduction morphism'''
    
    if not isinstance(bar_ecc_elements, set):
        bar_ecc_elements = {bar_ecc_elements}
    
    answer = set()
    for bar_ecc_element in bar_ecc_elements:
        d, a = len(bar_ecc_element)-1, max(bar_ecc_element[0]) #dimension and arity
        
        ordered_partitions = chain.from_iterable(
            set(permutations(p)) for p in partitions(d+a, d+1))
            
        for pi in ordered_partitions:
            
            surjection, removed = [], []
            degenerate = False
            for idx, i in enumerate(pi):
                 filtered =  [i for i in bar_ecc_element[idx] if i not in removed]
             
                 if idx > 0 and surjection[-1] == filtered[0]:
                     degenerate = True
                     break
                 
                 if i > 1:
                     removed += filtered[:i-1]
                     
                 surjection += filtered[:i]
        
            if not degenerate:
                answer ^= {tuple(surjection)}

    return answer

############ OPERADS ################

def surjection_operator(d, surjections):
    '''returns the set of multioperators representing the action of the passed 
    set of surjection on a d-simplex'''
    
    if not isinstance(surjections, set):
        surjections = set((surjections,))
     
    for surj in surjections:
        def _new_term(term, num_to_append, pos_to_append, k):
            tuple_to_replace = term['seq'][pos_to_append]+(num_to_append,)

            return {'pos': term['pos']+k, 
                    'seq': term['seq'][:pos_to_append] 
                            + (tuple_to_replace,)
                            + term['seq'][pos_to_append+1:]}

        after = [{'pos': 0, 
                  'seq': ((),)*(surj[0]-1) + ((0,),) + ((),)*(max(surj)-surj[0])}]

        for i in range(d+len(surj)-1):
            before = after[:]
            after = []
            for term in before:
                if term['pos'] < len(surj)-1:
                    num_to_append = term['seq'][surj[term['pos']]-1][-1]
                    pos_to_append = surj[term['pos']+1]-1

                    empty = bool(term['seq'][pos_to_append])
                    if not empty or num_to_append != term['seq'][pos_to_append][-1]:
                        after.append(_new_term(term, num_to_append, pos_to_append,1))

                if term['seq'][surj[term['pos']]-1][-1] < d:
                    num_to_append = term['seq'][surj[term['pos']]-1][-1] + 1
                    pos_to_append = surj[term['pos']]-1

                    after.append(_new_term(term, num_to_append, pos_to_append,0))

        answer = set()
        for term in after:
            operators = tuple()
            for seq in term['seq']:
                operators += (Operator(face_maps=[i for i in range(d+1) if i not in seq]),)
            answer ^= {operators}

    return answer

def barratt_eccles_operator(d, bar_ecc_elements):
    '''returns the multioperator defining the action of a barratt-eccles 
    element on simplices of dimension d'''
    
    if not isinstance(bar_ecc_elements, set):
        bar_ecc_elements = {bar_ecc_elements}
        
    answer = set()
    for bar_ecc_element in bar_ecc_elements:
        surjections = table_reduction(bar_ecc_element)
        for surjection in surjections:
            answer ^= surjection_operator(d, surjection)
        
    return answer

############# CARTAN ############

def cartan_operator(d, i):
    '''
    it returns the multioperators defining the i-th cartan coboundary in degree d when 
    applied to homogeneous cocycles
    '''
    
    def first_homotopy(n):
        '''applies the first homotopy to the element 
        \tilde x_n = (e, (12), ..., (12)^n)

        \sum_{i=0}^n ( (23)f(e), \dots,  (23)f((12)^i), g((12)^i), \dots, g((12)^n))

        (23)f(12) = (23)(13)(24) = (2,4,1,3)
            g(12) = (12)(34)     = (2,1,4,3)

        '''

        # permutations (23), (12)(34)(23) and e, (12)(34) 
        a = {0: (1,3,2,4), 1: (2,4,1,3)}
        b = {0: (1,2,3,4), 1: (2,1,4,3)}

        x = tuple(a[i%2] for i in range(n+1))
        y = tuple(b[i%2] for i in range(n+1))

        answer = set()
        for i in range(n+1):
            answer ^= {x[:i+1]+y[i:]}

        return answer

    def second_homotopy(n):
        '''
        applies the second homotopy to the element 
        \tilde x_n = (e, (12), ..., (12)^n)

        \circ_{\mathcal E}( (e, \dots, e) \otimes SHI (x \otimes x) )
        '''

        sigma_two = {0: (1,2), 1: (2,1)}
        x = [sigma_two[i%2] for i in range(n+1)]

        if n == 0:
            return set()

        # composition (e, x, y) with x,y in sigma_two
        composition = {((1,2), (2,1)) : (1,2,4,3),
                       ((2,1), (1,2)) : (2,1,3,4),
                       ((2,1), (2,1)) : (2,1,4,3),
                       ((1,2), (1,2)) : (1,2,3,4)}

        values = set()
        for op in shih(n):
            if not op.is_degenerate:
                values ^= {op(x)}

        answer = set()
        for value in values:

            table = tuple()
            for i in range(n+2):
                table += tuple((composition[(value[0][i], value[1][i])],))

            answer ^= {table}

        return answer

    all_operators = barratt_eccles_operator(d, first_homotopy(i)^second_homotopy(i))
    filtered_by_degree = {multiop for multiop in all_operators if 
                          multiop[0].degree == multiop[1].degree and 
                          multiop[2].degree == multiop[3].degree}
    
    return filtered_by_degree

