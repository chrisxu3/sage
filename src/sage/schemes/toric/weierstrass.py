r"""
Weierstrass form of a toric elliptic curve

There are 16 reflexive polygons in the plane, see
:func:`~sage.geometry.lattice_polytope.ReflexivePolytopes`. Each of
them defines a toric Fano variety. And each of them has a unique
crepant resolution to a smooth toric surface (Section 10.4 in [CLS2011]_) by
subdividing the face fan. An anticanonical hypersurface defines an
elliptic curve in this ambient space, which we call a toric elliptic
curve. The purpose of this module is to write an anticanonical
hypersurface equation in the short Weierstrass form `y^2 = x^3 + f x +
g`. This works over any base ring as long as its characteristic `\not=
2,3`.

For an analogous treatment of elliptic curves defined as complete
intersection in higher dimensional toric varieties, see
the module :mod:`~sage.schemes.toric.weierstrass_higher`.

Technically, this module computes the Weierstrass form of the Jacobian
of the elliptic curve. This is why you will never have to specify the
origin (or zero section) in the following.

It turns out [Bra2011]_ that the anticanonical hypersurface
equation of any one of the above 16 toric surfaces is a specialization
(that is, set one or more of the coefficients to zero) of the
following three cases. In inhomogeneous coordinates, they are

  * Cubic in `\mathbb{P}^2`:

    .. MATH::

        \begin{split}
          p(x,y) =&\;
          a_{30} x^{3} + a_{21} x^{2} y + a_{12} x y^{2} +
          a_{03} y^{3} + a_{20} x^{2} +
          \\ &\;
          a_{11} x y +
          a_{02} y^{2} + a_{10} x + a_{01} y + a_{00}
        \end{split}

  * Biquadric in `\mathbb{P}^1\times \mathbb{P}^1`:

    .. MATH::

        \begin{split}
          p(x,y) =&\;
          a_{22} x^2 y^2 + a_{21} x^2 y + a_{20} x^2 +
          a_{12} x y^2 +
          \\ &\;
          a_{11} x y + x a_{10} +
          y^2 a_{02} + y a_{01} + a_{00}
        \end{split}

  * Anticanonical hypersurface in weighted projective space
    `\mathbb{P}^2[1,1,2]`:

    .. MATH::

        \begin{split}
          p(x,y) =&\;
          a_{40} x^4 +
          a_{30} x^3 +
          a_{21} x^2 y +
          a_{20} x^2 +
          \\ &\;
          a_{11} x y +
          a_{02} y^2 +
          a_{10} x +
          a_{01} y +
          a_{00}
        \end{split}

EXAMPLES:

The main functionality is provided by :func:`WeierstrassForm`, which
brings each of the above hypersurface equations into Weierstrass
form::

    sage: R.<x,y> = QQ[]
    sage: cubic = x^3 + y^3 + 1
    sage: WeierstrassForm(cubic)
    (0, -27/4)
    sage: WeierstrassForm(x^4 + y^2 + 1)
    (-4, 0)
    sage: WeierstrassForm(x^2*y^2 + x^2 + y^2 + 1)
    (-16/3, 128/27)

Only the affine span of the Newton polytope of the polynomial
matters. For example::

    sage: R.<x,y,z> = QQ[]
    sage: WeierstrassForm(x^3 + y^3 + z^3)
    (0, -27/4)
    sage: WeierstrassForm(x * cubic)
    (0, -27/4)

This allows you to work with either homogeneous or inhomogeneous
variables. For example, here is the del Pezzo surface of degree 8::

    sage: dP8 = toric_varieties.dP8()
    sage: dP8.inject_variables()
    Defining t, x, y, z
    sage: WeierstrassForm(x*y^2 + y^2*z + t^2*x^3 + t^2*z^3)
    (-3, -2)
    sage: WeierstrassForm(x*y^2 + y^2 + x^3 + 1)
    (-3, -2)

By specifying only certain variables we can compute the Weierstrass
form over the polynomial ring generated by the remaining
variables. For example, here is a cubic over `\QQ[a]` ::

    sage: R.<a, x, y, z> = QQ[]
    sage: cubic = x^3 + a*y^3 + a^2*z^3
    sage: WeierstrassForm(cubic, variables=[x,y,z])
    (0, -27/4*a^6)

TESTS::

    sage: R.<f, g, x, y> = QQ[]
    sage: cubic = -y^2 + x^3 + f*x + g
    sage: WeierstrassForm(cubic, variables=[x,y])
    (f, g)

REFERENCES:

- [Bra2011]_
- [Du2010]_
- [ARVT2005]_
- [CLS2011]_
"""

########################################################################
#       Copyright (C) 2012 Volker Braun <vbraun.name@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  https://www.gnu.org/licenses/
########################################################################

from sage.misc.all import prod
from sage.rings.infinity import Infinity
from sage.modules.all import vector
from sage.geometry.polyhedron.ppl_lattice_polytope import LatticePolytope_PPL
from sage.rings.invariants.all import invariant_theory


######################################################################
#
#  Discriminant and j-invariant
#
######################################################################


def Discriminant(polynomial, variables=None):
    r"""
    The discriminant of the elliptic curve.

    INPUT:

    See :func:`WeierstrassForm` for how to specify the input
    polynomial(s) and variables.

    OUTPUT:

    The discriminant of the elliptic curve.

    EXAMPLES::

        sage: from sage.schemes.toric.weierstrass import Discriminant
        sage: R.<x, y, z> = QQ[]
        sage: Discriminant(x^3+y^3+z^3)
        19683/16
        sage: Discriminant(x*y*z)
        0
        sage: R.<w,x,y,z> = QQ[]
        sage: quadratic1 = w^2+x^2+y^2
        sage: quadratic2 = z^2 + w*x
        sage: Discriminant([quadratic1, quadratic2])
        -1/16
    """
    (f, g) = WeierstrassForm(polynomial, variables)
    return 4*f**3+27*g**2


######################################################################
def j_invariant(polynomial, variables=None):
    r"""
    Return the `j`-invariant of the elliptic curve.

    INPUT:

    See :func:`WeierstrassForm` for how to specify the input
    polynomial(s) and variables.

    OUTPUT:

    The j-invariant of the (irreducible) cubic. Notable special values:

      * The Fermat cubic: `j(x^3+y^3+z^3) = 0`

      * A nodal cubic: `j(-y^2 + x^2 + x^3) = \infty`

      * A cuspidal cubic `y^2=x^3` has undefined `j`-invariant. In this
        case, a ``ValueError`` is returned.

    EXAMPLES::

        sage: from sage.schemes.toric.weierstrass import j_invariant
        sage: R.<x,y,z> = QQ[]
        sage: j_invariant(x^3+y^3+z^3)
        0
        sage: j_invariant(-y^2 + x^2 + x^3)
        +Infinity
        sage: R.<x,y,z, a,b> = QQ[]
        sage: j_invariant( -y^2*z + x^3 + a*x*z^2, [x,y,z])
        1728

    TESTS::

        sage: j_invariant(x*y*z)
        Traceback (most recent call last):
        ...
        ValueError: curve is singular and has no well-defined j-invariant
    """
    (f, g) = WeierstrassForm(polynomial, variables)
    disc = 4*f**3+27*g**2
    if disc != 0:
        return 1728 * 4*f**3/disc
    if f != 0:
        return Infinity
    raise ValueError('curve is singular and has no well-defined j-invariant')


######################################################################
#
#  Weierstrass form of any elliptic curve
#
######################################################################
def Newton_polytope_vars_coeffs(polynomial, variables):
    """
    Return the Newton polytope in the given variables.

    INPUT:

    See :func:`WeierstrassForm` for how to specify the input
    polynomial and variables.

    OUTPUT:

    A dictionary with keys the integral values of the Newton polytope
    and values the corresponding coefficient of ``polynomial``.

    EXAMPLES::

        sage: from sage.schemes.toric.weierstrass import Newton_polytope_vars_coeffs
        sage: R.<x,y,z,a30,a21,a12,a03,a20,a11,a02,a10,a01,a00> = QQ[]
        sage: p = (a30*x^3 + a21*x^2*y + a12*x*y^2 + a03*y^3 + a20*x^2*z +
        ....:      a11*x*y*z + a02*y^2*z + a10*x*z^2 + a01*y*z^2 + a00*z^3)
        sage: p_data = Newton_polytope_vars_coeffs(p, [x,y,z]);  p_data
        {(0, 0, 3): a00,
         (0, 1, 2): a01,
         (0, 2, 1): a02,
         (0, 3, 0): a03,
         (1, 0, 2): a10,
         (1, 1, 1): a11,
         (1, 2, 0): a12,
         (2, 0, 1): a20,
         (2, 1, 0): a21,
         (3, 0, 0): a30}

        sage: from sage.geometry.polyhedron.ppl_lattice_polytope import LatticePolytope_PPL
        sage: polytope = LatticePolytope_PPL(list(p_data));  polytope
        A 2-dimensional lattice polytope in ZZ^3 with 3 vertices
        sage: polytope.vertices()
        ((0, 0, 3), (3, 0, 0), (0, 3, 0))
        sage: polytope.embed_in_reflexive_polytope()
        The map A*x+b with A=
        [-1 -1]
        [ 0  1]
        [ 1  0]
        b =
        (3, 0, 0)
    """
    R = polynomial.parent()
    var_indices = [R.gens().index(x) for x in variables]
    result = dict()
    for c, m in polynomial:
        e = m.exponents()[0]
        v = tuple([e[i] for i in var_indices])
        m_red = m // prod(x**i for x, i in zip(variables, v))
        result[v] = result.get(v, R.zero()) + c*m_red
    return result


######################################################################
def Newton_polygon_embedded(polynomial, variables):
    r"""
    Embed the Newton polytope of the polynomial in one of the three
    maximal reflexive polygons.

    This function is a helper for :func:`WeierstrassForm`

    INPUT:

    Same as :func:`WeierstrassForm` with only a single polynomial passed.

    OUTPUT:

    A tuple `(\Delta, P, (x,y))` where

    * `\Delta` is the Newton polytope of ``polynomial``.

    * `P(x,y)` equals the input ``polynomial`` but with redefined variables
      such that its Newton polytope is `\Delta`.

    EXAMPLES::

        sage: from sage.schemes.toric.weierstrass import Newton_polygon_embedded
        sage: R.<x,y,z> = QQ[]
        sage: cubic = x^3 + y^3 + z^3
        sage: Newton_polygon_embedded(cubic, [x,y,z])
        (A 2-dimensional lattice polytope in ZZ^3 with 3 vertices,
         x^3 + y^3 + 1,
         (x, y))

        sage: R.<a, x,y,z> = QQ[]
        sage: cubic = x^3 + a*y^3 + a^2*z^3
        sage: Newton_polygon_embedded(cubic, variables=[x,y,z])
        (A 2-dimensional lattice polytope in ZZ^3 with 3 vertices,
         a^2*x^3 + y^3 + a,
         (x, y))

        sage: R.<s,t,x,y> = QQ[]
        sage: biquadric = (s+t)^2 * (x+y)^2
        sage: Newton_polygon_embedded(biquadric, [s,t,x,y])
        (A 2-dimensional lattice polytope in ZZ^4 with 4 vertices,
         s^2*t^2 + 2*s^2*t + 2*s*t^2 + s^2 + 4*s*t + t^2 + 2*s + 2*t + 1,
         (s, t))
    """
    p_dict = Newton_polytope_vars_coeffs(polynomial, variables)
    newton_polytope = LatticePolytope_PPL(list(p_dict))
    assert newton_polytope.affine_dimension() <= 2
    embedding = newton_polytope.embed_in_reflexive_polytope('points')
    x, y = variables[0:2]
    embedded_polynomial = polynomial.parent().zero()
    for e, c in p_dict.items():
        e_embed = embedding[e]
        embedded_polynomial += c * x**(e_embed[0]) * y**(e_embed[1])
    return newton_polytope, embedded_polynomial, (x, y)


######################################################################
def WeierstrassForm(polynomial, variables=None, transformation=False):
    r"""
    Return the Weierstrass form of an elliptic curve inside either
    inside a toric surface or $\mathbb{P}^3$.

    INPUT:

    - ``polynomial`` -- either a polynomial or a list of polynomials
      defining the elliptic curve.
      A single polynomial can be either a cubic, a biquadric, or the
      hypersurface in `\mathbb{P}^2[1,1,2]`. In this case the
      equation need not be in any standard form, only its Newton
      polyhedron is used.
      If two polynomials are passed, they must both be quadratics in
      `\mathbb{P}^3`.

    - ``variables`` -- a list of variables of the parent polynomial
      ring or ``None`` (default). In the latter case, all variables
      are taken to be polynomial ring variables. If a subset of
      polynomial ring variables are given, the Weierstrass form is
      determined over the function field generated by the remaining
      variables.

    - ``transformation`` -- boolean (default: ``False``). Whether to
      return the new variables that bring ``polynomial`` into
      Weierstrass form.

    OUTPUT:

    The pair of coefficients `(f,g)` of the Weierstrass form `y^2 =
    x^3 + f x + g` of the hypersurface equation.

    If ``transformation=True``, a triple `(X,Y,Z)` of polynomials
    defining a rational map of the toric hypersurface or complete
    intersection in `\mathbb{P}^3` to its Weierstrass form in
    `\mathbb{P}^2[2,3,1]` is returned.
    That is, the triple satisfies

    .. MATH::

        Y^2 = X^3 + f X Z^4 + g Z^6

    when restricted to the toric hypersurface or complete intersection.

    EXAMPLES::

        sage: R.<x,y,z> = QQ[]
        sage: cubic = x^3 + y^3 + z^3
        sage: f, g = WeierstrassForm(cubic);  (f, g)
        (0, -27/4)

    Same in inhomogeneous coordinates::

        sage: R.<x,y> = QQ[]
        sage: cubic = x^3 + y^3 + 1
        sage: f, g = WeierstrassForm(cubic);  (f, g)
        (0, -27/4)

        sage: X,Y,Z = WeierstrassForm(cubic, transformation=True);  (X,Y,Z)
        (-x^3*y^3 - x^3 - y^3,
         1/2*x^6*y^3 - 1/2*x^3*y^6 - 1/2*x^6 + 1/2*y^6 + 1/2*x^3 - 1/2*y^3,
         x*y)

    Note that plugging in `[X:Y:Z]` to the Weierstrass equation is a
    complicated polynomial, but contains the hypersurface equation as
    a factor::

        sage: -Y^2 + X^3 + f*X*Z^4 + g*Z^6
        -1/4*x^12*y^6 - 1/2*x^9*y^9 - 1/4*x^6*y^12 + 1/2*x^12*y^3
        - 7/2*x^9*y^6 - 7/2*x^6*y^9 + 1/2*x^3*y^12 - 1/4*x^12 - 7/2*x^9*y^3
        - 45/4*x^6*y^6 - 7/2*x^3*y^9 - 1/4*y^12 - 1/2*x^9 - 7/2*x^6*y^3
        - 7/2*x^3*y^6 - 1/2*y^9 - 1/4*x^6 + 1/2*x^3*y^3 - 1/4*y^6
        sage: cubic.divides(-Y^2 + X^3 + f*X*Z^4 + g*Z^6)
        True

    Only the affine span of the Newton polytope of the polynomial
    matters. For example::

        sage: R.<x,y,z> = QQ[]
        sage: cubic = x^3 + y^3 + z^3
        sage: WeierstrassForm(cubic.subs(z=1))
        (0, -27/4)
        sage: WeierstrassForm(x * cubic)
        (0, -27/4)

    This allows you to work with either homogeneous or inhomogeneous
    variables. For example, here is the del Pezzo surface of degree 8::

        sage: dP8 = toric_varieties.dP8()
        sage: dP8.inject_variables()
        Defining t, x, y, z
        sage: WeierstrassForm(x*y^2 + y^2*z + t^2*x^3 + t^2*z^3)
        (-3, -2)
        sage: WeierstrassForm(x*y^2 + y^2 + x^3 + 1)
        (-3, -2)

    By specifying only certain variables we can compute the
    Weierstrass form over the function field generated by the
    remaining variables. For example, here is a cubic over `\QQ[a]` ::

        sage: R.<a, x,y,z> = QQ[]
        sage: cubic = x^3 + a*y^3 + a^2*z^3
        sage: WeierstrassForm(cubic, variables=[x,y,z])
        (0, -27/4*a^6)

    TESTS::

        sage: for P in ReflexivePolytopes(2):
        ....:     S = ToricVariety(FaceFan(P))
        ....:     p = sum((-S.K()).sections_monomials())
        ....:     print(WeierstrassForm(p))
        (-25/48, -1475/864)
        (-97/48, 17/864)
        (-25/48, -611/864)
        (-27/16, 27/32)
        (47/48, -199/864)
        (47/48, -71/864)
        (5/16, -21/32)
        (23/48, -235/864)
        (-1/48, 161/864)
        (-25/48, 253/864)
        (5/16, 11/32)
        (-25/48, 125/864)
        (-67/16, 63/32)
        (-11/16, 3/32)
        (-241/48, 3689/864)
        (215/48, -5291/864)
    """
    if isinstance(polynomial, (list, tuple)):
        from sage.schemes.toric.weierstrass_higher import WeierstrassForm2
        return WeierstrassForm2(polynomial, variables=variables, transformation=transformation)
    if transformation:
        from sage.schemes.toric.weierstrass_covering import WeierstrassMap
        return WeierstrassMap(polynomial, variables=variables)
    if variables is None:
        variables = polynomial.variables()
    from sage.geometry.polyhedron.ppl_lattice_polygon import (
        polar_P2_polytope, polar_P1xP1_polytope, polar_P2_112_polytope)
    newton_polytope, polynomial, variables = \
        Newton_polygon_embedded(polynomial, variables)
    polygon = newton_polytope.embed_in_reflexive_polytope('polytope')
    if polygon is polar_P2_polytope():
        return WeierstrassForm_P2(polynomial, variables)
    if polygon is polar_P1xP1_polytope():
        return WeierstrassForm_P1xP1(polynomial, variables)
    if polygon is polar_P2_112_polytope():
        return WeierstrassForm_P2_112(polynomial, variables)
    raise ValueError('Newton polytope is not contained in a reflexive polygon')


######################################################################
#
#  Weierstrass form of cubic in P^2
#
######################################################################
def _check_homogeneity(polynomial, variables, weights, total_weight=None):
    """
    Raise ``ValueError`` if the polynomial is not weighted
    homogeneous.

    INPUT:

    - ``polynomial`` -- the input polynomial. See
      :func:`WeierstrassForm` for details.

    - ``variables`` -- the variables.  See :func:`WeierstrassForm` for
      details.

    - ``weights`` -- list of integers, one per variable. the weights
      of the variables.

    - ``total_weight`` -- an integer or ``None`` (default). If an
      integer is passed, it is also checked that the weighted total
      degree of polynomial is this value.

    OUTPUT:

    This function returns nothing. If the polynomial is not weighted
    homogeneous, a ``ValueError`` is raised.

    EXAMPLES::

        sage: from sage.schemes.toric.weierstrass import _check_homogeneity
        sage: R.<x,y,z,a30,a21,a12,a03,a20,a11,a02,a10,a01,a00> = QQ[]
        sage: p = (a30*x^3 + a21*x^2*y + a12*x*y^2 + a03*y^3 + a20*x^2*z +
        ....:      a11*x*y*z + a02*y^2*z + a10*x*z^2 + a01*y*z^2 + a00*z^3)
        sage: _check_homogeneity(p, [x,y,z], (1,1,1), 3)

        sage: _check_homogeneity(p+x^4, [x,y,z], (1,1,1), 3)
        Traceback (most recent call last):
        ...
        ValueError: The polynomial is not homogeneous with weights (1, 1, 1)
    """
    w = vector(weights)
    n = w.degree()
    all_variables = polynomial.parent().gens()
    variable_indices = [all_variables.index(x) for x in variables]
    total_weight = None
    for e in polynomial.exponents():
        weight_e = sum(e[variable_indices[i]] * weights[i] for i in range(n))
        if total_weight is None:
            total_weight = weight_e
        else:
            if weight_e != total_weight:
                raise ValueError('The polynomial is not homogeneous with '
                                 'weights '+str(weights))


######################################################################
def _extract_coefficients(polynomial, monomials, variables):
    """
    Return the coefficients of ``monomials``.

    INPUT:

    - ``polynomial`` -- the input polynomial

    - ``monomials`` -- a list of monomials in the polynomial ring

    - ``variables`` -- a list of variables in the polynomial ring

    OUTPUT:

    A tuple containing the coefficients of the monomials in the given
    polynomial.

    EXAMPLES::

        sage: from sage.schemes.toric.weierstrass import _extract_coefficients
        sage: R.<x,y,z,a30,a21,a12,a03,a20,a11,a02,a10,a01,a00> = QQ[]
        sage: p = (a30*x^3 + a21*x^2*y + a12*x*y^2 + a03*y^3 + a20*x^2*z +
        ....:      a11*x*y*z + a02*y^2*z + a10*x*z^2 + a01*y*z^2 + a00*z^3)
        sage: m = [x^3, y^3, z^3, x^2*y, x^2*z, x*y^2, y^2*z, x*z^2, y*z^2, x*y*z]
        sage: _extract_coefficients(p, m, [x,y,z])
        (a30, a03, a00, a21, a20, a12, a02, a10, a01, a11)

        sage: m = [x^3, y^3, 1, x^2*y, x^2, x*y^2, y^2, x, y, x*y]
        sage: _extract_coefficients(p.subs(z=1), m, [x,y])
        (a30, a03, a00, a21, a20, a12, a02, a10, a01, a11)
    """
    R = polynomial.parent()
    indices = [R.gens().index(x) for x in variables]

    def index(monomial):
        if monomial in R.base_ring():
            return tuple(0 for i in indices)
        e = monomial.exponents()[0]
        return tuple(e[i] for i in indices)
    coeffs = dict()
    for c, m in polynomial:
        i = index(m)
        coeffs[i] = c*m + coeffs.pop(i, R.zero())
    result = tuple(coeffs.pop(index(m), R.zero()) // m for m in monomials)
    if coeffs:
        raise ValueError('The polynomial contains more monomials than '
                         'given: ' + str(coeffs))
    return result


######################################################################
def _check_polynomial_P2(cubic, variables):
    """
    Check the polynomial is weighted homogeneous in standard variables.

    INPUT:

    - ``cubic`` -- the input polynomial. See
      :func:`WeierstrassForm` for details.

    - ``variables`` -- the variables or ``None``.  See
      :func:`WeierstrassForm` for details.

    OUTPUT:

    This functions returns ``variables``, potentially guessed from the
    polynomial ring. A ``ValueError`` is raised if the polynomial is
    not homogeneous.

    EXAMPLES::

        sage: from sage.schemes.toric.weierstrass import _check_polynomial_P2
        sage: R.<x,y,z> = QQ[]
        sage: cubic = x^3+y^3+z^3
        sage: _check_polynomial_P2(cubic, [x,y,z])
        (x, y, z)
        sage: _check_polynomial_P2(cubic, None)
        (x, y, z)
        sage: _check_polynomial_P2(cubic.subs(z=1), None)
        (x, y, None)
        sage: R.<x,y,z,t> = QQ[]
        sage: cubic = x^3+y^3+z^3 + t*x*y*z
        sage: _check_polynomial_P2(cubic, [x,y,z])
        (x, y, z)
        sage: _check_polynomial_P2(cubic, [x,y,t])
        Traceback (most recent call last):
        ...
        ValueError: The polynomial is not homogeneous with weights (1, 1, 1)
    """
    if variables is None:
        variables = cubic.variables()
    if len(variables) == 3:
        x, y, z = variables
        _check_homogeneity(cubic, [x, y, z], (1, 1, 1), 3)
    elif len(variables) == 2:
        x, y = variables
        z = None
    else:
        raise ValueError('Need two or three variables, got '+str(variables))
    return (x, y, z)


######################################################################
def WeierstrassForm_P2(polynomial, variables=None):
    r"""
    Bring a cubic into Weierstrass form.

    Input/output is the same as :func:`WeierstrassForm`, except that
    the input polynomial must be a standard cubic in `\mathbb{P}^2`,

    .. MATH::

        \begin{split}
          p(x,y) =&\;
          a_{30} x^{3} + a_{21} x^{2} y + a_{12} x y^{2} +
          a_{03} y^{3} + a_{20} x^{2} +
          \\ &\;
          a_{11} x y +
          a_{02} y^{2} + a_{10} x + a_{01} y + a_{00}
        \end{split}

    EXAMPLES::

        sage: from sage.schemes.toric.weierstrass import WeierstrassForm_P2
        sage: R.<x,y,z> = QQ[]
        sage: WeierstrassForm_P2( x^3+y^3+z^3 )
        (0, -27/4)

        sage: R.<x,y,z, a,b> = QQ[]
        sage: WeierstrassForm_P2( -y^2*z+x^3+a*x*z^2+b*z^3, [x,y,z] )
        (a, b)

    TESTS::

        sage: R.<x,y,z,a30,a21,a12,a03,a20,a11,a02,a10,a01,a00> = QQ[]
        sage: p = ( a30*x^3 + a21*x^2*y + a12*x*y^2 + a03*y^3 + a20*x^2*z +
        ....:       a11*x*y*z + a02*y^2*z + a10*x*z^2 + a01*y*z^2 + a00*z^3 )
        sage: WeierstrassForm_P2(p, [x,y,z])
        (-1/48*a11^4 + 1/6*a20*a11^2*a02 - 1/3*a20^2*a02^2 - 1/2*a03*a20*a11*a10
         + 1/6*a12*a11^2*a10 + 1/3*a12*a20*a02*a10 - 1/2*a21*a11*a02*a10
         + a30*a02^2*a10 - 1/3*a12^2*a10^2 + a21*a03*a10^2 + a03*a20^2*a01
         - 1/2*a12*a20*a11*a01 + 1/6*a21*a11^2*a01 + 1/3*a21*a20*a02*a01
         - 1/2*a30*a11*a02*a01 + 1/3*a21*a12*a10*a01 - 3*a30*a03*a10*a01
         - 1/3*a21^2*a01^2 + a30*a12*a01^2 + a12^2*a20*a00 - 3*a21*a03*a20*a00
         - 1/2*a21*a12*a11*a00 + 9/2*a30*a03*a11*a00 + a21^2*a02*a00
         - 3*a30*a12*a02*a00,
         1/864*a11^6 - 1/72*a20*a11^4*a02 + 1/18*a20^2*a11^2*a02^2
         - 2/27*a20^3*a02^3 + 1/24*a03*a20*a11^3*a10 - 1/72*a12*a11^4*a10
         - 1/6*a03*a20^2*a11*a02*a10 + 1/36*a12*a20*a11^2*a02*a10
         + 1/24*a21*a11^3*a02*a10 + 1/9*a12*a20^2*a02^2*a10
         - 1/6*a21*a20*a11*a02^2*a10 - 1/12*a30*a11^2*a02^2*a10
         + 1/3*a30*a20*a02^3*a10 + 1/4*a03^2*a20^2*a10^2
         - 1/6*a12*a03*a20*a11*a10^2 + 1/18*a12^2*a11^2*a10^2
         - 1/12*a21*a03*a11^2*a10^2 + 1/9*a12^2*a20*a02*a10^2
         - 1/6*a21*a03*a20*a02*a10^2 - 1/6*a21*a12*a11*a02*a10^2
         + a30*a03*a11*a02*a10^2 + 1/4*a21^2*a02^2*a10^2
         - 2/3*a30*a12*a02^2*a10^2 - 2/27*a12^3*a10^3 + 1/3*a21*a12*a03*a10^3
         - a30*a03^2*a10^3 - 1/12*a03*a20^2*a11^2*a01 + 1/24*a12*a20*a11^3*a01
         - 1/72*a21*a11^4*a01 + 1/3*a03*a20^3*a02*a01 - 1/6*a12*a20^2*a11*a02*a01
         + 1/36*a21*a20*a11^2*a02*a01 + 1/24*a30*a11^3*a02*a01
         + 1/9*a21*a20^2*a02^2*a01 - 1/6*a30*a20*a11*a02^2*a01
         - 1/6*a12*a03*a20^2*a10*a01 - 1/6*a12^2*a20*a11*a10*a01
         + 5/6*a21*a03*a20*a11*a10*a01 + 1/36*a21*a12*a11^2*a10*a01
         - 3/4*a30*a03*a11^2*a10*a01 + 1/18*a21*a12*a20*a02*a10*a01
         - 3/2*a30*a03*a20*a02*a10*a01 - 1/6*a21^2*a11*a02*a10*a01
         + 5/6*a30*a12*a11*a02*a10*a01 - 1/6*a30*a21*a02^2*a10*a01
         + 1/9*a21*a12^2*a10^2*a01 - 2/3*a21^2*a03*a10^2*a01
         + a30*a12*a03*a10^2*a01 + 1/4*a12^2*a20^2*a01^2
         - 2/3*a21*a03*a20^2*a01^2 - 1/6*a21*a12*a20*a11*a01^2
         + a30*a03*a20*a11*a01^2 + 1/18*a21^2*a11^2*a01^2
         - 1/12*a30*a12*a11^2*a01^2 + 1/9*a21^2*a20*a02*a01^2
         - 1/6*a30*a12*a20*a02*a01^2 - 1/6*a30*a21*a11*a02*a01^2
         + 1/4*a30^2*a02^2*a01^2 + 1/9*a21^2*a12*a10*a01^2
         - 2/3*a30*a12^2*a10*a01^2 + a30*a21*a03*a10*a01^2
         - 2/27*a21^3*a01^3 + 1/3*a30*a21*a12*a01^3 - a30^2*a03*a01^3
         - a03^2*a20^3*a00 + a12*a03*a20^2*a11*a00 - 1/12*a12^2*a20*a11^2*a00
         - 3/4*a21*a03*a20*a11^2*a00 + 1/24*a21*a12*a11^3*a00
         + 5/8*a30*a03*a11^3*a00 - 2/3*a12^2*a20^2*a02*a00
         + a21*a03*a20^2*a02*a00 + 5/6*a21*a12*a20*a11*a02*a00
         - 3/2*a30*a03*a20*a11*a02*a00 - 1/12*a21^2*a11^2*a02*a00
         - 3/4*a30*a12*a11^2*a02*a00 - 2/3*a21^2*a20*a02^2*a00
         + a30*a12*a20*a02^2*a00 + a30*a21*a11*a02^2*a00
         - a30^2*a02^3*a00 + 1/3*a12^3*a20*a10*a00
         - 3/2*a21*a12*a03*a20*a10*a00 + 9/2*a30*a03^2*a20*a10*a00
         - 1/6*a21*a12^2*a11*a10*a00 + a21^2*a03*a11*a10*a00
         - 3/2*a30*a12*a03*a11*a10*a00 - 1/6*a21^2*a12*a02*a10*a00
         + a30*a12^2*a02*a10*a00 - 3/2*a30*a21*a03*a02*a10*a00
         - 1/6*a21*a12^2*a20*a01*a00 + a21^2*a03*a20*a01*a00
         - 3/2*a30*a12*a03*a20*a01*a00 - 1/6*a21^2*a12*a11*a01*a00
         + a30*a12^2*a11*a01*a00 - 3/2*a30*a21*a03*a11*a01*a00
         + 1/3*a21^3*a02*a01*a00 - 3/2*a30*a21*a12*a02*a01*a00
         + 9/2*a30^2*a03*a02*a01*a00 + 1/4*a21^2*a12^2*a00^2
         - a30*a12^3*a00^2 - a21^3*a03*a00^2
         + 9/2*a30*a21*a12*a03*a00^2 - 27/4*a30^2*a03^2*a00^2)
    """
    x, y, z = _check_polynomial_P2(polynomial, variables)
    cubic = invariant_theory.ternary_cubic(polynomial, x, y, z)
    F = polynomial.base_ring()
    S = cubic.S_invariant()
    T = cubic.T_invariant()
    return (27*S, -27/F(4)*T)


######################################################################
#
#  Weierstrass form of biquadric in P1 x P1
#
######################################################################
def _check_polynomial_P1xP1(biquadric, variables):
    """
    Check the polynomial is weighted homogeneous in standard variables.

    INPUT:

    - ``biquadric`` -- the input polynomial. See
      :func:`WeierstrassForm` for details.

    - ``variables`` -- the variables or ``None``.  See
      :func:`WeierstrassForm` for details.

    OUTPUT:

    This functions returns ``variables``, potentially guessed from the
    polynomial ring. A ``ValueError`` is raised if the polynomial is
    not homogeneous.

    EXAMPLES::

        sage: from sage.schemes.toric.weierstrass import _check_polynomial_P1xP1
        sage: R.<x0,x1,y0,y1> = QQ[]
        sage: biquadric = ( x0^2*y0^2 + x0*x1*y0^2*2 + x1^2*y0^2*3
        ....:    + x0^2*y0*y1*4 + x0*x1*y0*y1*5 + x1^2*y0*y1*6
        ....:    + x0^2*y1^2*7 + x0*x1*y1^2*8 )
        sage: _check_polynomial_P1xP1(biquadric, [x0,x1,y0,y1])
        [x0, x1, y0, y1]
        sage: _check_polynomial_P1xP1(biquadric, None)
        (x0, x1, y0, y1)
        sage: _check_polynomial_P1xP1(biquadric.subs(y0=1, y1=1), None)
        [x0, None, x1, None]
        sage: _check_polynomial_P1xP1(biquadric, [x0,y0,x1,y1])
        Traceback (most recent call last):
        ...
        ValueError: The polynomial is not homogeneous with weights (1, 1, 0, 0)
    """
    if variables is None:
        variables = biquadric.variables()
    if len(variables) == 4:
        _check_homogeneity(biquadric, variables, (1, 1, 0, 0), 2)
        _check_homogeneity(biquadric, variables, (0, 0, 1, 1), 2)
    elif len(variables) == 2:
        variables = [variables[0], None, variables[1], None]
    else:
        raise ValueError('Need two or four variables, got '+str(variables))
    return variables


######################################################################
def _partial_discriminant(quadric, y0, y1=None):
    """
    Return the partial discriminant wrt. `(y_0, y_1)`.

    INPUT:

    - ``quadric`` -- a biquadric.

    - ``y_0``, ``y_1`` -- the variables of the quadric. The ``y_1``
      variable can be omitted if the quadric is inhomogeneous.

    OUTPUT:

    A plane quartic in ``x0``, ``x1``.

    EXAMPLES::

        sage: R.<x0,x1,y0,y1,a00,a10,a20,a01,a11,a21,a02,a12,a22> = QQ[]
        sage: biquadric = ( x0^2*y0^2*a00 + x0*x1*y0^2*a10 + x1^2*y0^2*a20
        ....:    + x0^2*y0*y1*a01 + x0*x1*y0*y1*a11 + x1^2*y0*y1*a21
        ....:    + x0^2*y1^2*a02 + x0*x1*y1^2*a12 + x1^2*y1^2*a22 )
        sage: from sage.schemes.toric.weierstrass import _partial_discriminant
        sage: _partial_discriminant(biquadric, y0, y1)
        x0^4*a01^2 + 2*x0^3*x1*a01*a11 + x0^2*x1^2*a11^2
        + 2*x0^2*x1^2*a01*a21 + 2*x0*x1^3*a11*a21 + x1^4*a21^2
        - 4*x0^4*a00*a02 - 4*x0^3*x1*a10*a02 - 4*x0^2*x1^2*a20*a02
        - 4*x0^3*x1*a00*a12 - 4*x0^2*x1^2*a10*a12 - 4*x0*x1^3*a20*a12
        - 4*x0^2*x1^2*a00*a22 - 4*x0*x1^3*a10*a22 - 4*x1^4*a20*a22
        sage: _partial_discriminant(biquadric, x0, x1)
        y0^4*a10^2 - 4*y0^4*a00*a20 - 4*y0^3*y1*a20*a01
        + 2*y0^3*y1*a10*a11 + y0^2*y1^2*a11^2 - 4*y0^3*y1*a00*a21
        - 4*y0^2*y1^2*a01*a21 - 4*y0^2*y1^2*a20*a02 - 4*y0*y1^3*a21*a02
        + 2*y0^2*y1^2*a10*a12 + 2*y0*y1^3*a11*a12 + y1^4*a12^2
        - 4*y0^2*y1^2*a00*a22 - 4*y0*y1^3*a01*a22 - 4*y1^4*a02*a22
    """
    if y1 is None:
        monomials = (quadric.parent().one(), y0, y0**2)
        variables = [y0]
    else:
        monomials = (y1**2, y0*y1, y0**2)
        variables = [y0, y1]
    c = _extract_coefficients(quadric, monomials, variables)
    return c[1]**2 - 4*c[0]*c[2]


######################################################################
def WeierstrassForm_P1xP1(biquadric, variables=None):
    r"""
    Bring a biquadric into Weierstrass form

    Input/output is the same as :func:`WeierstrassForm`, except that
    the input polynomial must be a standard biquadric in `\mathbb{P}^2`,

    .. MATH::

        \begin{split}
          p(x,y) =&\;
          a_{40} x^4 +
          a_{30} x^3 +
          a_{21} x^2 y +
          a_{20} x^2 +
          \\ &\;
          a_{11} x y +
          a_{02} y^2 +
          a_{10} x +
          a_{01} y +
          a_{00}
        \end{split}

    EXAMPLES::

        sage: from sage.schemes.toric.weierstrass import WeierstrassForm_P1xP1
        sage: R.<x0,x1,y0,y1>= QQ[]
        sage: biquadric = ( x0^2*y0^2 + x0*x1*y0^2*2 + x1^2*y0^2*3
        ....:    + x0^2*y0*y1*4 + x0*x1*y0*y1*5 + x1^2*y0*y1*6
        ....:    + x0^2*y1^2*7 + x0*x1*y1^2*8 )
        sage: WeierstrassForm_P1xP1(biquadric, [x0, x1, y0, y1])
        (1581/16, -3529/32)

    Since there is no `x_1^2 y_1^2` term in ``biquadric``, we can
    dehomogenize it and get a cubic::

        sage: from sage.schemes.toric.weierstrass import WeierstrassForm_P2
        sage: WeierstrassForm_P2(biquadric(x0=1,y0=1))
        (1581/16, -3529/32)

    TESTS::

        sage: R.<x0,x1,y0,y1,a00,a10,a20,a01,a11,a21,a02,a12,a22> = QQ[]
        sage: biquadric = ( x0^2*y0^2*a00 + x0*x1*y0^2*a10 + x1^2*y0^2*a20
        ....:    + x0^2*y0*y1*a01 + x0*x1*y0*y1*a11 + x1^2*y0*y1*a21
        ....:    + x0^2*y1^2*a02 + x0*x1*y1^2*a12 )
        sage: WeierstrassForm_P1xP1(biquadric, [x0, x1, y0, y1])
        (-1/48*a11^4 + 1/6*a01*a11^2*a21 - 1/3*a01^2*a21^2
         + 1/6*a20*a11^2*a02 + 1/3*a20*a01*a21*a02 - 1/2*a10*a11*a21*a02
         + a00*a21^2*a02 - 1/3*a20^2*a02^2 - 1/2*a20*a01*a11*a12
         + 1/6*a10*a11^2*a12 + 1/3*a10*a01*a21*a12 - 1/2*a00*a11*a21*a12
         + 1/3*a10*a20*a02*a12 - 1/3*a10^2*a12^2 + a00*a20*a12^2, 1/864*a11^6
         - 1/72*a01*a11^4*a21 + 1/18*a01^2*a11^2*a21^2 - 2/27*a01^3*a21^3
         - 1/72*a20*a11^4*a02 + 1/36*a20*a01*a11^2*a21*a02
         + 1/24*a10*a11^3*a21*a02 + 1/9*a20*a01^2*a21^2*a02
         - 1/6*a10*a01*a11*a21^2*a02 - 1/12*a00*a11^2*a21^2*a02
         + 1/3*a00*a01*a21^3*a02 + 1/18*a20^2*a11^2*a02^2
         + 1/9*a20^2*a01*a21*a02^2 - 1/6*a10*a20*a11*a21*a02^2
         + 1/4*a10^2*a21^2*a02^2 - 2/3*a00*a20*a21^2*a02^2 - 2/27*a20^3*a02^3
         + 1/24*a20*a01*a11^3*a12 - 1/72*a10*a11^4*a12
         - 1/6*a20*a01^2*a11*a21*a12 + 1/36*a10*a01*a11^2*a21*a12
         + 1/24*a00*a11^3*a21*a12 + 1/9*a10*a01^2*a21^2*a12
         - 1/6*a00*a01*a11*a21^2*a12 - 1/6*a20^2*a01*a11*a02*a12
         + 1/36*a10*a20*a11^2*a02*a12 + 1/18*a10*a20*a01*a21*a02*a12
         - 1/6*a10^2*a11*a21*a02*a12 + 5/6*a00*a20*a11*a21*a02*a12
         - 1/6*a00*a10*a21^2*a02*a12 + 1/9*a10*a20^2*a02^2*a12
         + 1/4*a20^2*a01^2*a12^2 - 1/6*a10*a20*a01*a11*a12^2
         + 1/18*a10^2*a11^2*a12^2 - 1/12*a00*a20*a11^2*a12^2
         + 1/9*a10^2*a01*a21*a12^2 - 1/6*a00*a20*a01*a21*a12^2
         - 1/6*a00*a10*a11*a21*a12^2 + 1/4*a00^2*a21^2*a12^2
         + 1/9*a10^2*a20*a02*a12^2 - 2/3*a00*a20^2*a02*a12^2
         - 2/27*a10^3*a12^3 + 1/3*a00*a10*a20*a12^3)

        sage: _ == WeierstrassForm_P1xP1(biquadric.subs(x1=1,y1=1), [x0, y0])
        True
    """
    x, y, s, t = _check_polynomial_P1xP1(biquadric, variables)
    delta = _partial_discriminant(biquadric, s, t)
    Q = invariant_theory.binary_quartic(delta, x, y)
    g2 = Q.EisensteinD()
    g3 = -Q.EisensteinE()
    return (-g2/4, -g3/4)


######################################################################
#
#  Weierstrass form of anticanonical hypersurface in WP2[1,1,2]
#
######################################################################
def _check_polynomial_P2_112(polynomial, variables):
    """
    Check the polynomial is weighted homogeneous in standard variables.

    INPUT:

    - ``polynomial`` -- the input polynomial. See
      :func:`WeierstrassForm` for details.

    - ``variables`` -- the variables or ``None``.  See
      :func:`WeierstrassForm` for details.

    OUTPUT:

    This functions returns ``variables``, potentially guessed from the
    polynomial ring. A ``ValueError`` is raised if the polynomial is
    not homogeneous.

    EXAMPLES::

        sage: from sage.schemes.toric.weierstrass import _check_polynomial_P2_112
        sage: R.<x,y,z,t> = QQ[]
        sage: polynomial = z^4*t^2 + x*z^3*t^2 + x^2*z^2*t^2 + x^3*z*t^2 + \
        ....:              x^4*t^2 + y*z^2*t + x*y*z*t + x^2*y*t + y^2
        sage: _check_polynomial_P2_112(polynomial, [x,y,z,t])
        (x, y, z, t)
        sage: _check_polynomial_P2_112(polynomial, None)
        (x, y, z, t)
        sage: _check_polynomial_P2_112(polynomial(z=1, t=1), None)
        (x, y, None, None)
        sage: _check_polynomial_P2_112(polynomial, [x,y,t,z])
        Traceback (most recent call last):
        ...
        ValueError: The polynomial is not homogeneous with weights (1, 0, 1, -2)
    """
    if variables is None:
        variables = polynomial.variables()
    else:
        variables = tuple(variables)
    if len(variables) == 4:
        _check_homogeneity(polynomial, variables, (1, 0, 1, -2), 0)
        _check_homogeneity(polynomial, variables, (0, 1, 0, 1), 2)
    elif len(variables) == 2:
        variables = tuple([variables[0], variables[1], None, None])
    else:
        raise ValueError('Need two or four variables, got '+str(variables))
    return variables


def WeierstrassForm_P2_112(polynomial, variables=None):
    r"""
    Bring an anticanonical hypersurface in `\mathbb{P}^2[1,1,2]` into Weierstrass form.

    Input/output is the same as :func:`WeierstrassForm`, except that
    the input polynomial must be a standard anticanonical hypersurface
    in weighted projective space `\mathbb{P}^2[1,1,2]`:

    .. MATH::

        \begin{split}
          p(x,y) =&\;
          a_{40} x^4 +
          a_{30} x^3 +
          a_{21} x^2 y +
          a_{20} x^2 +
          \\ &\;
          a_{11} x y +
          a_{02} y^2 +
          a_{10} x +
          a_{01} y +
          a_{00}
        \end{split}

    EXAMPLES::

        sage: from sage.schemes.toric.weierstrass import WeierstrassForm_P2_112
        sage: fan = Fan(rays=[(1,0),(0,1),(-1,-2),(0,-1)],cones=[[0,1],[1,2],[2,3],[3,0]])
        sage: P112.<x,y,z,t> = ToricVariety(fan)
        sage: (-P112.K()).sections_monomials()
        (z^4*t^2, x*z^3*t^2, x^2*z^2*t^2, x^3*z*t^2,
         x^4*t^2, y*z^2*t, x*y*z*t, x^2*y*t, y^2)
        sage: WeierstrassForm_P2_112(sum(_), [x,y,z,t])
        (-97/48, 17/864)

    TESTS::

        sage: R.<x,y,z,t,a40,a30,a20,a10,a00,a21,a11,a01,a02> = QQ[]
        sage: p = ( a40*x^4*t^2 + a30*x^3*z*t^2 + a20*x^2*z^2*t^2 + a10*x*z^3*t^2 +
        ....:       a00*z^4*t^2 + a21*x^2*y*t + a11*x*y*z*t + a01*y*z^2*t + a02*y^2 )
        sage: WeierstrassForm_P2_112(p, [x,y,z,t])
        (-1/48*a11^4 + 1/6*a21*a11^2*a01 - 1/3*a21^2*a01^2 + a00*a21^2*a02
         - 1/2*a10*a21*a11*a02 + 1/6*a20*a11^2*a02 + 1/3*a20*a21*a01*a02
         - 1/2*a30*a11*a01*a02 + a40*a01^2*a02 - 1/3*a20^2*a02^2 + a30*a10*a02^2
         - 4*a40*a00*a02^2, 1/864*a11^6 - 1/72*a21*a11^4*a01
         + 1/18*a21^2*a11^2*a01^2 - 2/27*a21^3*a01^3 - 1/12*a00*a21^2*a11^2*a02
         + 1/24*a10*a21*a11^3*a02 - 1/72*a20*a11^4*a02 + 1/3*a00*a21^3*a01*a02
         - 1/6*a10*a21^2*a11*a01*a02 + 1/36*a20*a21*a11^2*a01*a02
         + 1/24*a30*a11^3*a01*a02 + 1/9*a20*a21^2*a01^2*a02
         - 1/6*a30*a21*a11*a01^2*a02 - 1/12*a40*a11^2*a01^2*a02
         + 1/3*a40*a21*a01^3*a02 + 1/4*a10^2*a21^2*a02^2
         - 2/3*a20*a00*a21^2*a02^2 - 1/6*a20*a10*a21*a11*a02^2
         + a30*a00*a21*a11*a02^2 + 1/18*a20^2*a11^2*a02^2
         - 1/12*a30*a10*a11^2*a02^2 - 2/3*a40*a00*a11^2*a02^2
         + 1/9*a20^2*a21*a01*a02^2 - 1/6*a30*a10*a21*a01*a02^2
         - 4/3*a40*a00*a21*a01*a02^2 - 1/6*a30*a20*a11*a01*a02^2
         + a40*a10*a11*a01*a02^2 + 1/4*a30^2*a01^2*a02^2
         - 2/3*a40*a20*a01^2*a02^2 - 2/27*a20^3*a02^3
         + 1/3*a30*a20*a10*a02^3 - a40*a10^2*a02^3 - a30^2*a00*a02^3
         + 8/3*a40*a20*a00*a02^3)

        sage: _ == WeierstrassForm_P2_112(p.subs(z=1,t=1), [x,y])
        True

        sage: cubic = p.subs(a40=0)
        sage: a,b = WeierstrassForm_P2_112(cubic, [x,y,z,t])
        sage: a = a.subs(t=1,z=1)
        sage: b = b.subs(t=1,z=1)
        sage: from sage.schemes.toric.weierstrass import WeierstrassForm_P2
        sage: (a,b) == WeierstrassForm_P2(cubic.subs(t=1,z=1), [x,y])
        True
    """
    x, y, z, t = _check_polynomial_P2_112(polynomial, variables)
    delta = _partial_discriminant(polynomial, y, t)
    Q = invariant_theory.binary_quartic(delta, x, z)
    g2 = Q.EisensteinD()
    g3 = -Q.EisensteinE()
    return (-g2/4, -g3/4)
