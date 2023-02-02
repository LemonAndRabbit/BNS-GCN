python main.py \
  --dataset cora \
  --fix-seed \
  --seed 0 \
  --dropout 0. \
  --lr 0.003 \
  --n-partitions 2 \
  --n-epochs 100 \
  --model graphsage \
  --n-layers 2 \
  --n-hidden 32 \
  --log-every 1 \
  --sampling-rate 0.5 \
  --use-pp \
  --sampler=first \
  --n-feat 1433 \
  --n-class 7 \
  --n-train 2708 \
  --skip-partition
