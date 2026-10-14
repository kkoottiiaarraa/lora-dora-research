"""Known thin-SVD and RTN storage controls for fixed-D adapters; no training."""


def thin_factors(left, right, rank):
    import torch
    if left.ndim != 2 or right.ndim != 2 or left.shape[1] != right.shape[0]:
        raise ValueError('Unaligned factors')
    if not 0 < rank <= min(left.shape[1], left.shape[0], right.shape[1]):
        raise ValueError('Invalid rank')
    ql, rl = torch.linalg.qr(left.double(), mode='reduced')
    qr, rr = torch.linalg.qr(right.double().T, mode='reduced')
    u, s, vh = torch.linalg.svd(rl @ rr.T, full_matrices=False)
    sq = s[:rank].sqrt()
    return ((ql @ u[:, :rank]) * sq).float().contiguous(), (
        sq[:, None] * (vh[:rank] @ qr.T)).float().contiguous()


def quantize_component(value, dimension):
    import torch
    if dimension not in (0, 1) or value.ndim != 2 or not bool(value.isfinite().all()):
        raise ValueError('Finite matrix and explicit reduction dimension required')
    maximum = value.abs().amax(dim=dimension, keepdim=True)
    scale = torch.where(maximum > 0, maximum / 127., torch.ones_like(maximum)).float()
    codes = (value / scale).round().clamp(-127, 127).to(torch.int8).contiguous()
    return codes, scale.contiguous()


def encode(left, right, row_scale, mode):
    import torch
    if row_scale.shape != (left.shape[0],) or left.shape[1] != right.shape[0]:
        raise ValueError('Record shape mismatch')
    if not all(bool(t.isfinite().all()) for t in (left, right, row_scale)):
        raise FloatingPointError('Nonfinite input')
    result = {'row_scale': row_scale.float().contiguous()}
    if mode == 'fp16':
        result.update(left=left.half().contiguous(), right=right.half().contiguous())
    elif mode == 'int8':
        result['left'], result['left_scale'] = quantize_component(left, 0)
        result['right'], result['right_scale'] = quantize_component(right, 1)
    else:
        raise ValueError('Unknown storage mode')
    if not all(bool(t.isfinite().all()) for t in result.values()):
        raise FloatingPointError('Storage overflow')
    return result


def decode(record):
    expected = {'left', 'right', 'row_scale'}
    quantized = 'left_scale' in record
    if quantized:
        expected |= {'left_scale', 'right_scale'}
    if set(record) != expected:
        raise ValueError('Incomplete encoded record')
    import torch
    if quantized:
        if record['left'].dtype != torch.int8 or record['right'].dtype != torch.int8:
            raise ValueError('INT8 codes required')
        for name in ('left_scale', 'right_scale'):
            if record[name].dtype != torch.float32 or not bool((record[name] > 0).all()):
                raise ValueError('Positive FP32 quantization scales required')
        left = record['left'].float() * record['left_scale']
        right = record['right'].float() * record['right_scale']
    else:
        if record['left'].dtype != torch.float16 or record['right'].dtype != torch.float16:
            raise ValueError('FP16 storage factors required')
        left, right = record['left'].float(), record['right'].float()
    if record['row_scale'].dtype != torch.float32:
        raise ValueError('FP32 D required')
    result = dict(left=left.contiguous(), right=right.contiguous(), row_scale=record['row_scale'])
    if not all(bool(t.isfinite().all()) for t in result.values()):
        raise FloatingPointError('Nonfinite decoded factor')
    return result


def payload_bytes(records):
    return sum(t.numel() * t.element_size() for rec in records.values() for t in rec.values())
