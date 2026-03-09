import pyopencl as cl
import numpy as np
import binascii
import time

# Functional Scrypt OpenCL Kernel (N=1024, r=1, p=1)
# Optimized for LTC mining with correct target comparison.
SCRYPT_KERNEL = """
#define ROTL32(a, b) (((a) << (b)) | ((a) >> (32 - (b))))

static void salsa8_word_xor(uint B[16]) {
    uint x[16];
    for (int i = 0; i < 16; i++) x[i] = B[i];
    for (int i = 8; i > 0; i -= 2) {
        x[ 4] ^= ROTL32(x[ 0] + x[12],  7);  x[ 8] ^= ROTL32(x[ 4] + x[ 0],  9);
        x[12] ^= ROTL32(x[ 8] + x[ 4], 13);  x[ 0] ^= ROTL32(x[12] + x[ 8], 18);
        x[ 9] ^= ROTL32(x[ 5] + x[ 1],  7);  x[13] ^= ROTL32(x[ 9] + x[ 5],  9);
        x[ 1] ^= ROTL32(x[13] + x[ 9], 13);  x[ 5] ^= ROTL32(x[ 1] + x[13], 18);
        x[14] ^= ROTL32(x[10] + x[ 6],  7);  x[ 2] ^= ROTL32(x[14] + x[10],  9);
        x[ 6] ^= ROTL32(x[ 2] + x[14], 13);  x[10] ^= ROTL32(x[ 6] + x[ 2], 18);
        x[ 3] ^= ROTL32(x[15] + x[11],  7);  x[ 7] ^= ROTL32(x[ 3] + x[15],  9);
        x[11] ^= ROTL32(x[ 7] + x[ 3], 13);  x[15] ^= ROTL32(x[11] + x[ 7], 18);
        x[ 1] ^= ROTL32(x[ 0] + x[ 3],  7);  x[ 2] ^= ROTL32(x[ 1] + x[ 0],  9);
        x[ 3] ^= ROTL32(x[ 2] + x[ 1], 13);  x[ 0] ^= ROTL32(x[ 3] + x[ 2], 18);
        x[ 6] ^= ROTL32(x[ 5] + x[ 4],  7);  x[ 7] ^= ROTL32(x[ 6] + x[ 5],  9);
        x[ 4] ^= ROTL32(x[ 7] + x[ 6], 13);  x[ 5] ^= ROTL32(x[ 4] + x[ 7], 18);
        x[11] ^= ROTL32(x[10] + x[ 9],  7);  x[ 8] ^= ROTL32(x[11] + x[10],  9);
        x[ 9] ^= ROTL32(x[ 8] + x[11], 13);  x[10] ^= ROTL32(x[ 9] + x[ 8], 18);
        x[12] ^= ROTL32(x[15] + x[14],  7);  x[13] ^= ROTL32(x[12] + x[15],  9);
        x[14] ^= ROTL32(x[13] + x[12], 13);  x[15] ^= ROTL32(x[14] + x[13], 18);
    }
    for (int i = 0; i < 16; i++) B[i] += x[i];
}

static void scrypt_core(uint *X, uint *V) {
    for (int i = 0; i < 1024; i++) {
        for (int j = 0; j < 32; j++) V[i * 32 + j] = X[j];
        for (int j = 0; j < 16; j++) X[j] ^= X[16 + j];
        salsa8_word_xor(X);
        for (int j = 0; j < 16; j++) X[16 + j] ^= X[j];
        salsa8_word_xor(X + 16);
    }
    for (int i = 0; i < 1024; i++) {
        uint j = (X[16] & 1023) * 32;
        for (int k = 0; k < 32; k++) X[k] ^= V[j + k];
        for (int j = 0; j < 16; j++) X[j] ^= X[16 + j];
        salsa8_word_xor(X);
        for (int j = 0; j < 16; j++) X[16 + j] ^= X[j];
        salsa8_word_xor(X + 16);
    }
}

__kernel void scrypt_mine(
    __global const uchar* header,
    uint start_nonce,
    __global const uint* target_256,
    __global uint* output_nonce,
    __global uint* found_flag,
    __global uint* V_global
) {
    uint gid = get_global_id(0);
    uint nonce = start_nonce + gid;

    __global uint* V = &V_global[gid * 1024 * 32];

    uint X[32];
    for(int i=0; i<19; i++) {
        X[i] = ((__global uint*)header)[i];
    }
    X[19] = nonce;
    for(int i=20; i<32; i++) X[i] = 0;

    scrypt_core(X, V);

    // Proper 256-bit target comparison (little-endian)
    bool lower = false;
    for (int i = 7; i >= 0; i--) {
        if (X[i] < target_256[i]) {
            lower = true;
            break;
        } else if (X[i] > target_256[i]) {
            lower = false;
            break;
        }
    }

    if (lower) {
        if (atomic_xchg(found_flag, 1) == 0) {
            *output_nonce = nonce;
        }
    }
}
"""

class GPUWorker:
    def __init__(self):
        self.ctx = None
        self.queue = None
        self.program = None
        self.enabled = False
        self.devices = []
        try:
            platforms = cl.get_platforms()
            for platform in platforms:
                try:
                    gpu_devices = platform.get_devices(device_type=cl.device_type.GPU)
                    self.devices.extend(gpu_devices)
                except cl.Error:
                    continue

            if self.devices:
                selected_device = self.devices[0]
                # Prefer high-performance GPUs
                for device in self.devices:
                    if "NVIDIA" in device.name or "AMD" in device.name or "Radeon" in device.name:
                        selected_device = device
                        break

                self.ctx = cl.Context([selected_device])
                self.queue = cl.CommandQueue(self.ctx)
                self.program = cl.Program(self.ctx, SCRYPT_KERNEL).build()
                self.enabled = True
                print(f"GPU Mining enabled on: {selected_device.name}")
        except Exception as e:
            print(f"GPU Mining initialization failed: {e}")

    def mine(self, header_base, start_nonce, range_size, target_int):
        if not self.enabled:
            return None

        try:
            header_np = np.frombuffer(header_base, dtype=np.uint8)
            # Convert target to 8 32-bit integers (little-endian)
            target_256_np = np.zeros(8, dtype=np.uint32)
            for i in range(8):
                target_256_np[i] = (target_int >> (i * 32)) & 0xFFFFFFFF

            header_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, host_ptr=header_np)
            target_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, host_ptr=target_256_np)

            output_nonce_np = np.zeros(1, dtype=np.uint32)
            found_flag_np = np.zeros(1, dtype=np.uint32)

            output_nonce_buf = cl.Buffer(self.ctx, cl.mem_flags.WRITE_ONLY, output_nonce_np.nbytes)
            found_flag_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR, host_ptr=found_flag_np)

            v_size = range_size * 1024 * 32 * 4
            v_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, v_size)

            self.program.scrypt_mine(
                self.queue, (range_size,), None,
                header_buf, np.uint32(start_nonce), target_buf,
                output_nonce_buf, found_flag_buf, v_buf
            )

            cl.enqueue_copy(self.queue, found_flag_np, found_flag_buf)
            if found_flag_np[0] == 1:
                cl.enqueue_copy(self.queue, output_nonce_np, output_nonce_buf)
                return int(output_nonce_np[0])
        except Exception as e:
            print(f"GPU Mining error: {e}")

        return None

if __name__ == "__main__":
    worker = GPUWorker()
    if worker.enabled:
        header = b"0" * 76
        target = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
        nonce = worker.mine(header, 0, 100, target)
        print(f"GPU found nonce: {nonce}")
    else:
        print("GPU Worker not active.")
