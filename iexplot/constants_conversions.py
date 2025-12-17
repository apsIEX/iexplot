def T_K2meV(Temp_K, verbose=False):
    """
    convert the temperature in K to energy in meV
    kB = 8.617333262E-5 (eV/K)  
    """
    kB = 8.617333262E-5 #eV/K   
    meV = kB*Temp_K*1000
    if verbose:
        print("kB*T(K) = "+str(meV)+" meV")
    return 

def imfp(hv):
    """
    returns the inelastic mean free path in nm using the universal curve impf 143/hv**2 + 0.054*sqrt(hv)  
    hv = photon energy in eV
    """
    return 143/hv**2 + 0.054*sqrt(hv)