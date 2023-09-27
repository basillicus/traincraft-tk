#!python

"""
Parse an aims.out file and extract the geoemtries and forces of a geometry optimization
Returns an .extxyz file
"""

outfile = 'geom_optim_history.extxyz'
init_geom = 'aims.out'

lattice_vector = []
atoms = []
forces = []

# Parse the output file
with open(init_geom) as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if 'Number of atoms' in line:
            n_atoms = int(line.split()[5])
        if 'Number of lattice vectors' in line:
            n_lattice_vectors = int(line.split()[6])
        if 'lattice_vector' in line:
            lattice_vector.append(line)
        if '  atom  ' in line:
            atoms.append(line)
        if 'Total atomic forces' in line:
            forces.append(lines[i+1:i+1+n_atoms])

# Create the extxyz outputfile
fout = open(outfile, 'w')
steps = len(forces)
step = 0

#               step      atom     force components
# print(forces[steps-1][n_atoms-1].split()[2:5])

while step < steps:
    fout.write(f'{n_atoms}\n')

    # Work out the comment line of the extxyz file
    idx_lattice_vector = step * n_lattice_vectors
    tmp = []
    for vec in range(n_lattice_vectors):
        tmp.append(lattice_vector[idx_lattice_vector + vec].split()[1:4])

    ilattice = ''
    for lat in tmp:
        ilattice += ' '.join(lat)
        ilattice += ' '

    # TODO: Work the pbc bit to handle pbc="F F T" or F F F
    fout.write('Lattice="' + ilattice + '"  pbc="T T T"\n')

    # Write atoms with their forces
    idx_atoms = step * n_atoms
    for atom in range(n_atoms):
        # print(comment.join(lattice_vector[idx_lattice_vector + vec].split()[1:]))
        iatom = atoms[idx_atoms + atom].split()[1:4]
        ispecies = str(atoms[idx_atoms + atom].split()[4])
        iforces = forces[step][atom].split()[2:5]
        fout.write(ispecies + '\t' + '\t'.join(iatom) + '\t' + '\t'.join(iforces) + '\n')
    step += 1

print('Geometry optimization steps: ', steps)
