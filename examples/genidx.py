#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utilities for converting indices.

Created on Fri Mar 24 13:21:07 2017

@author: Juha Jeronen, juha.jeronen@tut.fi
"""

import numpy as np


# These generalize to the nD case given below.
#
#def genidx2D( nx,ny ):
#    """Generate index vectors to meshgrid and corresponding raveled array."""
#    i = range(nx)
#    j = range(ny)
#    I,J = np.meshgrid( i,j, indexing='ij' )
#    Ilin = np.reshape(I,-1)
#    Jlin = np.reshape(J,-1)
#    IJ = np.ravel_multi_index( (Ilin,Jlin), (nx,ny) )
#    return (Ilin,Jlin,IJ)
#
#def genidx3D( nx,ny,nz ):
#    """Generate index vectors to meshgrid and corresponding raveled array."""
#    i = range(nx)
#    j = range(ny)
#    k = range(nz)
#    I,J,K = np.meshgrid( i,j,k, indexing='ij' )
#    Ilin = np.reshape(I,-1)
#    Jlin = np.reshape(J,-1)
#    Klin = np.reshape(K,-1)
#    IJK = np.ravel_multi_index( (Ilin,Jlin,Klin), (nx,ny,nz) )
#    return (Ilin,Jlin,Klin,IJK)

def genidx( shp ):
    """Generate index vectors to meshgrid and corresponding raveled array.

Parameters:
shp:
    tuple of int, shape of the meshgrid (nx, ny, nz, ...)

Returns:
tuple I_0, I_1, ..., I_{n-1}, R, where
    I_0, I_1, ..., I_{n-1}:
        rank-1 arrays to index each dimension of the meshgrid as M[I_0, I_1, ..., I_{n-1}]

    R:
        rank-1 array of corresponding indices to corresponding raveled array

so that M[I_0[j], I_1[j], ..., I_{n-1}[j]] and raveled[R[j]] denote the same grid point.
"""
    if np.array(shp).ndim > 1:
        raise ValueError("shp must be a list or a rank-1 array")

    # Create index vectors for each dimension of the grid.
    #
    # Note that
    #
    #    shp = (n_0, n_1, ..., n_{d-1})
    #
    # The kth vector has length shp[k].
    #
    i = [ range(nk) for nk in shp ]

    # Create the meshgrid:
    #
    #     I = (I_0, I_1, ..., I_{d-1})
    #
    # where each I_k is a rank-d array of shape shp (accepting a multi-index of d dimensions),
    # where the value is the grid point index on the kth axis.
    #
    # This is used just to generate all prod(shp) combinations of the per-axis indices.
    #
    I = np.meshgrid( *i, indexing='ij' )

    # Flatten the meshgrid to remove grid structure, so that the tuple
    #
    #     pj = ( Ilin[0][j], Ilin[1][j], ..., Ilin[-1][j] )
    #
    # gives the indices, on each axis, of the jth grid point.
    #
    # Each Ilin[k]:
    # - is a rank-1 array of length prod(shp).
    # - takes on values in the range 0, 1, ..., shp[k]-1.
    #
    # Ilin is now the multi-index.
    #
    Ilin = [ Ik.reshape(-1) for Ik in I ]

    # Generate the raveled index that corresponds to the multi-index.
    #
    # This numbers the grid points sequentially.
    #
    R = np.ravel_multi_index( Ilin, shp )

    out = list(Ilin)  # just for semantic tidiness; we don't actually need a copy
                      # as the original Ilin is no longer needed
    out.append( R )
    return out

