_base_ = [
    '../_base_/models/fpn_snn_r50.py',
    # '../_base_/models/fpn_r50.py',
    '../_base_/datasets/ade20k.py',
    '../_base_/default_runtime.py',
    '../_base_/schedules/schedule_160k.py'
]
# These setting is well used, copy before using!!!
# model settings
norm_cfg = dict(type='SyncBN', requires_grad=True)
crop_size = (512, 512)
data_preprocessor = dict(size=crop_size)
checkpoint_file = '/home/shensicheng/code/Spike-Driven-Transformer-V3/SDT_V3/Segmentation/ckpt/V3_19.0M_1x4.pth'

model = dict(
    data_preprocessor=data_preprocessor,
    type='EncoderDecoder',
    backbone=dict(
        init_cfg=dict(type='Pretrained', checkpoint=checkpoint_file),
        type='Spiking_vit_MetaFormerv2',
        img_size_h=512,
        img_size_w=512,
        patch_size=16,
        embed_dim=[64, 128, 256, 360],
        num_heads=8,
        mlp_ratios=4,
        in_channels=3,
        num_classes=150,
        qkv_bias=False,
        depths=8,
        sr_ratios=1,
        T=4,
        decode_mode='QTrick',
    ),
    neck=dict(
        in_channels=[32, 64, 128, 360],
        out_channels=128,
        T=4,
        act_cfg=None),
    decode_head=dict(
        in_channels=[128, 128, 128, 128],
        channels=128,
        num_classes=150,
        T=4,
        act_cfg=None))

# load_from = checkpoint_file
gpu_multiples = 1  # we use 8 gpu instead of 4 in mmsegmentation, so lr*2 and max_iters/2
# optimizer

optim_wrapper = dict(
    _delete_=True,
    type='OptimWrapper',
    optimizer=dict(
        type='AdamW', lr=0.001, betas=(0.9, 0.999), weight_decay=0.005),
    paramwise_cfg=dict(
        custom_keys={
            'head': dict(lr_mult=2.)}
    ))
#
param_scheduler = [
    dict(
        type='LinearLR', start_factor=1e-6, by_epoch=False, begin=0, end=1500),
    dict(
        type='PolyLR',
        eta_min=0.0,
        power=1.0,
        begin=1500,
        end=160000,
        by_epoch=False,
    )
]
# policy='poly', power=0.9, min_lr=0.0, by_epoch=False
optimizer_config = dict()
# learning policy
lr_config = dict(warmup_iters=1500)
# runtime settings

train_cfg = dict(
    type='IterBasedTrainLoop', max_iters=160000, val_interval=8000)
train_dataloader = dict(batch_size=16)
val_dataloader = dict(batch_size=1)
test_dataloader = val_dataloader

default_hooks = dict(
    timer=dict(type='IterTimerHook'),
    logger=dict(type='LoggerHook', interval=50, log_metric_by_epoch=False),
    param_scheduler=dict(type='ParamSchedulerHook'),
    checkpoint=dict(
        type='CheckpointHook', by_epoch=False, interval=10000,
        save_best='mIoU'),
    )

work_dir = '/home/shensicheng/log/SpikingTransformerBenchmark/seg/SDTv3/'