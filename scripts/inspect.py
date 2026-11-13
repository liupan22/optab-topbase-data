import sys
import h5py

fn = sys.argv[1]
with h5py.File(fn, 'r') as f:
    def walk(name, obj):
        if isinstance(obj, h5py.Dataset):
            print('DS ', name, obj.shape, obj.dtype)
        else:
            print('GRP', name)
    f.visititems(walk)
    print('attrs root:', dict(f.attrs))
