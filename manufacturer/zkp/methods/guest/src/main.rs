use risc0_zkvm::guest::env;

const MAX_STR_LEN: usize = 32;

struct Product {
    id: u32,
    name: [u8; MAX_STR_LEN],
    volume: u32,
    certified: bool,
    sender: [u8; MAX_STR_LEN],
}

fn bytes_to_string(bytes: &[u8; 32]) -> String {
    let len = bytes.iter().position(|&b| b == 0).unwrap_or(bytes.len());
    String::from_utf8(bytes[..len].to_vec()).unwrap()
}

fn str_to_bytes(s: &str) -> [u8; MAX_STR_LEN] {
    let mut bytes = [0u8; MAX_STR_LEN];
    let s_bytes = s.as_bytes();
    let len = s_bytes.len().min(MAX_STR_LEN);
    bytes[..len].copy_from_slice(&s_bytes[..len]);
    bytes
}

fn main() {
    let (id, name_bytes, volume): (u32, [u8; MAX_STR_LEN], u32) = env::read();
    let name = bytes_to_string(&name_bytes); 

    let product = Product {
        id,
        name: str_to_bytes(&name),
        volume,
        certified: false,
        sender: str_to_bytes("Manufacturer A"),
    };

    env::commit(&(
        product.id,
        product.name,
        product.volume,
        product.certified,
        product.sender,
    ));
}
