from helper.parser import *
import random
import torch.multiprocessing as mp
import sys
import subprocess
from helper.utils import *
import train

if __name__ == '__main__':

    args = create_parser()
    if args.fix_seed is False:
        args.seed = random.randint(0, 1 << 31)

    g, n_feat, n_class = load_data(args.dataset)

    args.n_class = n_class
    args.n_feat = n_feat
    args.n_train = g.ndata['train_mask'].int().sum().item()

    if args.inductive:
        args.graph_name = '%s-%d-%s-induc' % (args.dataset, args.n_partitions, args.partition_method)
    else:
        args.graph_name = '%s-%d-%s-trans' % (args.dataset, args.n_partitions, args.partition_method)

    print(args)

    if args.inductive:
        graph_partition(g.subgraph(g.ndata['train_mask']), args)
    else:
        graph_partition(g, args)

    if args.backend == 'gloo':
        processes = []
        if 'CUDA_VISIBLE_DEVICES' in os.environ:
            devices = os.environ['CUDA_VISIBLE_DEVICES'].split(',')
        else:
            n = torch.cuda.device_count()
            devices = [f'{i}' for i in range(n)]
        mp.set_start_method('spawn', force=True)
        for i in range(args.n_partitions):
            os.environ['CUDA_VISIBLE_DEVICES'] = devices[i % len(devices)]
            p = mp.Process(target=train.init_processes, args=(i, args.n_partitions, args))
            p.start()
            processes.append(p)
        for p in processes:
            p.join()
    elif args.backend == 'mpi':
        gcn_arg = []
        for k, v in vars(args).items():
            if v is True:
                gcn_arg.append(f'--{k}')
            elif v is not False:
                gcn_arg.extend([f'--{k}', f'{v}'])
        mpi_arg = []
        mpi_arg.extend(['-n', f'{args.n_partitions}'])
        command = ['mpirun'] + mpi_arg + ['python', 'train.py'] + gcn_arg
        print(' '.join(command))
        subprocess.run(command, stderr=sys.stderr, stdout=sys.stdout)
    else:
        raise ValueError
