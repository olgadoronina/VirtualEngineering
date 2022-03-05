import pt
import matplotlib.pyplot as plt
import numpy as np
import pt_input_file_io as pt_input
import timeit as timerlib
import subprocess

import sys
from vebio.Utilities import dict_to_yaml, yaml_to_dict

# run pretreatment model
inputfilename='pretreat_defs.inp'
outputfilebase = 'ptsim_'


inputfile = open(inputfilename, 'r')

meshp, scales, IBCs, rrates, Egtcs, deto =\
    pt_input.readinpfile('pretreat_defs.inp')


# If applicable, load the input file into a dictionary
if len(sys.argv) > 1:
    params_filename = sys.argv[1]
    ve_params = yaml_to_dict(params_filename)
    # print(ve_params)

    # read in final time in order to calculate a "print time"
    finaltime = ve_params['pretreatment_input']['final_time']
    N = 10 # could make this a user preference
    prnttime = finaltime/(N-1) + 0.001*finaltime

    # Override pretreat_defs.inp definitions with those from the pretreatment widgets
    IBCs['acid'] = ve_params['pretreatment_input']['initial_acid_conc']
    IBCs['stmT'] = ve_params['pretreatment_input']['steam_temperature']
    IBCs['bkst'] = ve_params['pretreatment_input']['bulk_steam_conc']
    meshp['ftime'] = finaltime
    meshp['ptime'] = prnttime
    IBCs['xyfr'] = ve_params['feedstock']['xylan_solid_fraction']
    IBCs['lifr'] = 1.0 - ve_params['pretreatment_input']['initial_solid_fraction']
    IBCs['poro'] = ve_params['feedstock']['initial_porosity']
    # trial-and-error adjustment to model parameters to account for auger
    # reactor rather than steam-explosion reactor -- didn't end up using any
    # adjustments, but keeping in case we want to try in the future
    #Egtcs['chtr'] = 0.01 # "convective heat transfer", original: 0.5
    #deto['togs'] = 5.0 # "tortuosity gas", original:  1.0
    #deto['toli'] = 5.0 # "turtuosity liquid", original:  1.0
    #rrates['stdf'][0] = 5 # "pore diameter", original:  15
    #scales['xscl'] = 5.0 # "length scale", original:  1.0
    # ratemult = 0.1 
    # rrates['kxylog'][0] = ratemult*rrates['kxylog'][0]
    # rrates['kxyl1'][0] = ratemult*rrates['kxyl1'][0]
    # rrates['kxyl2'][0] = ratemult*rrates['kxyl2'][0]
    # rrates['kfurf'][0] = ratemult*rrates['kfurf'][0]
else:
    ve_params = {}


# read in number of elements from input file
nelem = meshp['enum']

ppelem = meshp['ppnts']
gneq = 7

# calculate the shape of the output array
m = nelem*(ppelem - 1) + 1
n = gneq + 1


#establish parameters for porosity and time dependent [acid] calcs
fx0 = IBCs['xyfr'] # initial fraction of xylan in the solids, a.k.a., X_X0 
ep0 = IBCs['poro']
cacid0 = IBCs['acid']
eL0 = IBCs['lifr']
l = meshp['maxx']

new_inputfilename = 'pretreat_defs_updated.inp'
pt_input.writeinpfile(new_inputfilename, meshp, scales, IBCs, rrates, Egtcs, deto)

# run the simulation
simtime=-timerlib.default_timer()
# Make the call to pt.main(m, n, filename) using subprocess
command = f'python pt_solve.py {m} {n} {new_inputfilename}'
out = subprocess.run(command.split(), capture_output=True, text=True)
solnvec = np.genfromtxt('pt_solnvec.csv', delimiter=',')
assert np.shape(solnvec) == (m, n)
simtime=simtime+timerlib.default_timer()

#solnvec=pt.ptmain.interpsoln
n=len(solnvec)

x=solnvec[:,0]
steam=solnvec[:,1]
liquid=solnvec[:,2]
Temp=solnvec[:,3]
xylan=solnvec[:,4] # what is this? units? dimensionless concentration? what
                   # basis? JJS 3/22/20
xylog=solnvec[:,5]
xylose=solnvec[:,6]
furfural=solnvec[:,7]
porosity=ep0+fx0*(1.0-ep0)-xylan
cacid = cacid0*eL0/liquid

# integrate concentrations to determine bulk xylose, xylog, and furfural concentrations
solidvfrac = 1.0-porosity
xylanweight = np.trapz(xylan,x)
solidweight = np.trapz(solidvfrac,x)
liquid_bulk = np.trapz(liquid,x)
gas_bulk    = np.trapz(porosity-liquid,x)

xylan_bulk    = xylanweight/solidweight # this looks like X_X (fraction of solids)?
xylose_bulk   = np.trapz(xylose,x)/liquid_bulk
xylog_bulk    = np.trapz(xylog,x)/liquid_bulk
furfural_bulk = np.trapz(furfural,x)/liquid_bulk
steam_bulk    = np.trapz(steam*(porosity-liquid),x)/gas_bulk

M_xylose = 150.0
M_furf   = 100.0
M_xylog  = 450.0


xylanweight0 = fx0*(1-ep0)*l
#print( "initial xylan mass   (density =  1 g/ml):%4.4g" %    xylanweight0)
#print( "final xylan mass     (density =  1 g/ml):%4.4g" %    xylanweight)
#print( "reacted xylan mass   (density =  1 g/ml):%4.4g" %    (fx0*(1-ep0)*l-xylanweight))

prodmass = liquid_bulk*(xylose_bulk*M_xylose + xylog_bulk*M_xylog + furfural_bulk*M_furf)
reactmass = xylanweight0 - xylanweight
conv = reactmass/xylanweight0  # I _think_ this is correct now, but should be
                               # double-checked, JJS 3/14/21
# compute an updated glucan fraction based on xylan conversion
X_G = ve_params['feedstock']['glucan_solid_fraction']/(1 - ve_params['feedstock']['xylan_solid_fraction']*conv)


print( "\n**************************************************************************")
#print( "xylan weight: %4.4g" %       xylanweight) # again, what are the units?
#print( "solid weight: %4.4g" %       solidweight)
print( "[Xylan] (w/w) %4.4g" %       xylan_bulk)
print( "[Glucan] (w/w) %4.4g" %       X_G)
#print( "[xylose] (M/ml) =%4.4g" %   xylose_bulk)
print( "[xylose] (g/L) =%4.4g" %    (xylose_bulk*1000*M_xylose))
#print( "[xylog] (M/ml) =%4.4g" %    xylog_bulk)
print( "[xylog] (g/L) =%4.4g" %     (xylog_bulk*1000*M_xylog))
#print( "[furfural] (M/ml) =%4.4g" % furfural_bulk)
print( "[furfural] (g/L) =%4.4g" %  (furfural_bulk*1000*M_furf))
#print( "Avg. liquid = %4.4g" %       liquid_bulk)
#print( "Avg. gas    = %4.4g" %       gas_bulk)
#print( "weight of steam added per 1g of initial liquid: %4.4g" % ((liquid_bulk-eL0*l)/(eL0*l)))
print( "Fraction of Insoluble solids: %4.4g" % (solidweight/(solidweight+liquid_bulk)))
print( "simulation time: %4.4g seconds" %(simtime))
print( "**************************************************************************\n\n")
print( "Mass balance calculations")
print( "*************************")

#print( "liquid weight (density = 1 g/ml): %4.4g" % liquid_bulk)
#print( "liquid volume (density = 1 g/ml): %4.4g" % liquid_bulk)
#print( "xylose mass                     : %4.4g" % (liquid_bulk*xylose_bulk*M_xylose))
#print( "xylooligomer mass               : %4.4g" % (liquid_bulk*xylog_bulk*M_xylog))
#print( "furfural mass                   : %4.4g" % (liquid_bulk*furfural_bulk*M_furf))
#print( "total mass of products          : %4.4g" % prodmass)
print( "total xylan conversion (%%)      : %4.4g" % (100*conv))
print( "%% mass balance                  : %4.4g" % (100*(1.0-(prodmass-reactmass)/reactmass)))

# Save the outputs into a dictionary
output_dict = {'pretreatment_output': {}}
output_dict['pretreatment_output']['fis_0'] = float(solidweight/(solidweight+liquid_bulk))
output_dict['pretreatment_output']['conv'] = float(conv)
output_dict['pretreatment_output']['X_X'] = float(xylan_bulk) # is this correct? JJS 3/22/20
output_dict['pretreatment_output']['X_G'] = float(X_G)
# adding xylo-oligomers to xylose, based on the assumption that these will be
# converted to xylose during enzymatic hydrolysis (otherwise, these sugars are
# "lost"), JJS 3/21/21
output_dict['pretreatment_output']['rho_x'] = float(xylose_bulk*1000*M_xylose
                                                    + xylog_bulk*1000*M_xylog)
output_dict['pretreatment_output']['rho_f'] = float(furfural_bulk*1000*M_furf)
output_dict['pretreatment_output']['rho_f_init'] = float(furfural[0])
output_dict['pretreatment_output']['rho_f_final'] = float(furfural[-1])

if len(sys.argv) > 1:
    dict_to_yaml([ve_params, output_dict], params_filename)

# if len(sys.argv) > 2:
#     # Save the output dictionary to a .yaml file
#     output_filename = sys.argv[2]
#     dict_to_yaml(output_dict, output_filename)
