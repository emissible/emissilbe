import numpy as np
import os
import pubchempy as pcp
import scipy.signal

# import the Molecule class
from core import Molecule 

"""
The data obtaining functions.  Please note that many of these functions
should only need to be run when training a new model.
"""

#data_dir global variable containing the path to the data
def get_emission_files(data_dir):
  """
  Get the total files containing emission spectra.  Expects the files to be of
  type *.ems.txt and have the naming convention *.ems.txt will return a list
  of strings to be parsed later.
  """
  return [fn for fn in os.listdir(data_dir) if fn.endswith(".ems.txt")]

def get_absorption_files(data_dir):
  """
  Get the total files containing absorption spectra.  Expects the files to be
  of type *.txt and have the naming convention *.abs.txt will return a list of
  strings to be parsed later.
  """
  return [fn for fn in os.listdir(data_dir) if fn.endswith(".abs.txt")]

def get_molecule_cid(file_name):
  """ 
  Take a file_name, remove the ending and prefix and return the pubchem
  molecule object.  If the file_name does not have the cas number, try the name
  of the system,   else return None so as to disreguard the molecule
  from training.
  """
  my_file = file_name.split("_")
  #try to get the cas # if not then try name.
  cas = my_file[1]
  try:
    cid = pcp.get_compounds(cas, 'name')[0]
  except:
    #file doesn't have a cas number with it, try name
    my_name = cas.split(".")
    try:
      cid = pcp.get_compounds(my_name[0], 'name')[0]
    except:
      cid = None
  finally:
    return cid

def get_spectra(file_name):
  """
  Iterates through the file and pulls out the normalized spectrum contained
  within.  The X is in wavelentgh, and the intensity is normalized to the
  most intense peak.
  """
  spectra = []
  with open (file_name,'r') as file:
    next(file)
    for line in file:
      tmp = line.split()
      if len(tmp) > 1:
        spectra.append([float(tmp[0]), float(tmp[1])])
      else:
        continue
  return np.asarray(spectra)

def get_peaks(spectra):
  peaks = []
  """
  This will take in the spectra from the get_spectra function and will return
  a list of [x,Y] coordinates for the peaks.
  """
  peak_locations = scipy.signal.find_peaks(spectra[:,1])[0]
  for i in peak_locations:
    peaks.append(spectra[i, :])
  return np.asarray(peaks)

def initiate_molecules(data_dir):
  """
  Takes in the directory containing all of the data files and returns a list
  of populated molecule objects.
  """
  
  my_molecules = []
  my_added_molecules = []
  #For all applicable emission spectra put properties into molecule objects,
  #and place objects into list for molecules.
  for ems_file in get_emission_files(data_dir):
    pubchem_molecule = get_molecule_cid(ems_file) 
    if pubchem_molecule:
      cid = pubchem_molecule.cid
      spectra = get_spectra(data_dir + "/" + ems_file)
      absorp = None
      columb = None
      emiss = get_peaks(spectra)
      smiles = pubchem_molecule.isomeric_smiles
      weight = pubchem_molecule.molecular_weight
      file_name = ems_file.split(".")[0]
      my_molecules.append(Molecule(absorp, cid, columb, emiss, smiles, weight,\
        file_name))
      my_added_molecules.append(cid)
    else:
      pass
  #For all applicable absorption spectra put properties into molecule objects,
  #and place objects into list for molecules.
  for abs_file in get_absorption_files(data_dir):
    found = 0
    cid = get_molecule_cid(abs_file)
    #Check to see if the molecule already exists in the list, and if it does
    #does it already have valid absorption peaks:
    if pubchem_molecule:
      cid = pubchem_molecule.cid
      if cid in my_added_molecules:
        found = 1
        mol_index = my_added_molecules.index(cid)
        spectra = get_spectra(data_dir + "/" + abs_file)
        my_molecules[mol_index].absorption_peaks = get_peaks(spectra)
        break
      else:
        pass
      if not found:
        spectra = get_spectra(data_dir + "/" + abs_file)
        absorp = get_peaks(spectra)
        columb = None
        emiss = None
        smiles = pubchem_molecule.isomeric_smiles
        weight = pubchem_molecule.molecular_weight
        file_name = abs_file.split(".")[0]
        my_molecules.append(Molecule(absorp, cid, columb, emiss, smiles, \
          weight, file_name))
  return my_molecules

def electrostatic_potentials(file_name):
  potential = None
  return potential