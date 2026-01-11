import secretflow as sf
import sys
import yaml
import time

# Check parameters
if len(sys.argv) < 7:
    print("Usage: python run_psi.py <cluster_yaml> <alice_in> <bob_in> <alice_out> <bob_out> <join_key>")
    sys.exit(1)

config_file = sys.argv[1]
alice_in    = sys.argv[2]
bob_in      = sys.argv[3]
alice_out   = sys.argv[4]
bob_out     = sys.argv[5]
join_key    = sys.argv[6]

# 1. Load configuration
with open(config_file, 'r') as f:
    cluster_conf = yaml.safe_load(f)

# 2. Initialize SecretFlow (Establish Ray Connections)
sf.init(
    address='local', 
    cluster_config={
        'parties': cluster_conf['parties'],
        'self_party': cluster_conf['self_party']
    }
)
print(f"[{cluster_conf['self_party']}] SF Init successful.")

# 3. Initialize the SPU device
spu_conf_def = cluster_conf.get('spu_config')
if spu_conf_def is None:
    print("Error: The spu_config field is missing from the YAML file.")
    sf.shutdown()
    sys.exit(1)

spu = sf.SPU(cluster_def=spu_conf_def)
print(f"[{cluster_conf['self_party']}] SPU Init successful.")

# 4. Prepare PSI parameters (construct dictionary)
input_path = {"alice": alice_in, "bob": bob_in}
output_path = {"alice": alice_out, "bob": bob_out}
# keys need to be a List[str], so we put each key into the list.
psi_keys = {"alice": [join_key], "bob": [join_key]}

print("------------------------------------------------------")
print(f"Start executing PSI.")
print(f"Alice Input: {alice_in} -> Output: {alice_out}")
print(f"Bob   Input: {bob_in}   -> Output: {bob_out}")
print("------------------------------------------------------")

try:
    # 5. Execute PSI
    report = spu.psi(
        keys=psi_keys,
        input_path=input_path,
        output_path=output_path,
        receiver="alice", 
        broadcast_result=True,
        protocol='PROTOCOL_RR22', 
        ecdh_curve='CURVE_25519'# If the protocol is switched back to ECDH and this is required, RR22 does not strongly depend on this.
    )
    
    print(f"✅ PSI execution complete!")
    print(f"📊 Report: {report}")

except Exception as e:
    print(f"❌ An error occurred: {e}")
    raise
finally:
    # 6. 关闭连接
    sf.shutdown()
    print("SF Shutdown complete.")