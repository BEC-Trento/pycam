import numpy as np

class BackgroundManager():
    def __init__(self,):
        self.sis_path_list = None
        self.B_dataset = None
        self.imshape = None
        self.mask = None
        self.beta = None
        self.BB_inv = None
    
    def load_dataset(self, path_list):
        self.sis_path_list = path_list
        # _l = []
        # for p in path_list:
        #     b = self.readsis_simple(p)[1]
        #     _l.append(b)
        _l = [self.readsis_simple(p)[1] for p in path_list]
        B_dataset = np.concatenate([b[np.newaxis, :,:] for b in _l], axis=0)
        self.imshape = B_dataset[0].shape
        self.B_dataset = B_dataset
        # return B_dataset
    
    def load_mask(self, mask):
        self.mask = mask
        
    def compute_bg_matrix(self,):
        if self.B_dataset is None:
            print('You must load a dataset first')
            return
        if self.mask is None:    
            print('You must set a mask first')
            return
        beta = np.concatenate([b[self.mask][np.newaxis, :] for b in self.B_dataset], axis=0)
        BB = np.dot(beta, beta.T)
        try:
            BB_inv = np.linalg.inv(BB)
        except np.linalg.LinAlgError as err:
            print('BB matrix is singular: will pseudo-invert')
            BB_inv = np.linalg.pinv(BB)
        self.beta = beta
        self.BB_inv = BB_inv
        # return beta, BB_inv

    def compute_opt_backround(self, image, output_coeff=False):
        alpha = np.dot(self.beta, image[self.mask])
        c = np.dot(self.BB_inv, alpha)
        B_opt = np.sum(self.B_dataset*c[:, np.newaxis, np.newaxis], axis=0)
        if output_coeff:
            return c, B_opt
        else:
            return B_opt
        
    def readsis_simple(self, filename, dtype=np.float):
        f = open(filename, 'rb')                        # open in reading and binary mode
        rawdata = np.fromfile(f,'H').astype(dtype)
        # 'H' = uint16
        # types are listed in np.typeDict
        # put in an array the data formatted uint16 and casted to int
        ''' NB fundamental to cast to int:
            unsigned short gives overflow '''
        f.close()
        width=int(rawdata[6])  # N cols
        height=int(rawdata[5]) # N rows
        # Reading the images
        image = rawdata[-width*height:].copy()
        image.resize(height,width)
        # defines the two images in the sis
        im0 = image[:height//2, :]
        im1 = image[height//2:, :]
        return im0, im1

    
def _readsis(filename, dtype=np.float):
    f = open(filename, 'rb')                        # open in reading and binary mode
    rawdata = np.fromfile(f,'H').astype(dtype)
    # 'H' = uint16
    # types are listed in np.typeDict
    # put in an array the data formatted uint16 and casted to int
    ''' NB fundamental to cast to int:
            unsigned short gives overflow '''
    f.close()
    width=int(rawdata[6])  # N cols
    height=int(rawdata[5]) # N rows
    # Reading the images
    image = rawdata[-width*height:].copy()
    image.resize(height,width)
    # defines the two images in the sis
    im0 = image[:height//2, :]
    im1 = image[height//2:, :]
    return im0, im1


def _writesis(OD, filename, self=0, Bheight=0, Bwidth=0, stamp='xxx'):
        #norm = np.array((2,1))
        norm = np.append(OD.min(), OD.max())
        par = OD + abs(norm[0])
        image = par * 6553.6
        #image = par.astype(np.uint16)
        print(norm.astype(np.uint16))

        #keep the double-image convention for sis files, filling the unused
        #with zeros
        if self == 0:
            image = np.concatenate((image, np.zeros_like(image)))
        elif self == 1:
            image = np.concatenate((np.zeros_like(image), image))

        with open(str(filename), 'w+b') as fid:
            # Write here SisV2 + other 4 free bytes
            head = 'SisV2' + '.' + '0'*4
            fid.write(head.encode())

            # This is OK
            height, width = image.shape
            size = np.array([height, width], dtype=np.uint16)
            size.tofile(fid)

            # Here we put 2*2 more bytes with the sub-block dimension
            Bsize = np.array([Bheight, Bwidth], dtype=np.uint16)
            Bsize.tofile(fid)

            # Also a timestamp
            ts = time.time()
            phead = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.')
            fid.write(phead.encode())

            # More: descriptive stamp
            ls = np.array([len(stamp)], dtype=np.uint16) # length of the stamp coded at the 38+39 byte
            ls.tofile(fid)
            fid.write(stamp.encode())
            freeHead = '0'*(472-len(stamp))
            fid.write(freeHead.encode())

            image.astype(np.uint16).tofile(fid)
