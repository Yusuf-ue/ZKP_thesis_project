use methods::{GUEST_CODE_FOR_ZK_PROOF_ELF, GUEST_CODE_FOR_ZK_PROOF_ID};
use risc0_zkvm::{default_prover, ExecutorEnv};
use serde::{Serialize, Deserialize};
use serde_json;
use std::io::{self, Read};
use bincode;
use base64::{engine::general_purpose, Engine as _};

const MAX_STR_LEN: usize = 32;

fn bytes_to_string(bytes: &[u8; MAX_STR_LEN]) -> String {
    let len = bytes.iter().position(|&b| b == 0).unwrap_or(MAX_STR_LEN);
    String::from_utf8(bytes[..len].to_vec()).unwrap()
}

// Product structure for JSON output
#[derive(Debug, Serialize)]
struct Product {
    id: u32,
    name: String,
    volume: u32,
    certified: bool,
    sender: String,
}

#[derive(Deserialize)]
struct ProductInput {
    id: u32,
    name: String,
    volume: u32,
}

fn main() {
    tracing_subscriber::fmt()
        .with_env_filter(tracing_subscriber::filter::EnvFilter::from_default_env())
        .init();

    let mut input_json = String::new();
    io::stdin().read_to_string(&mut input_json).unwrap();
    let input: ProductInput = serde_json::from_str(&input_json).unwrap();

    let product_id = input.id;

    let mut name_bytes = [0u8; MAX_STR_LEN];
    let name_slice = input.name.as_bytes();
    name_bytes[..name_slice.len().min(MAX_STR_LEN)]
        .copy_from_slice(&name_slice[..name_slice.len().min(MAX_STR_LEN)]);

    let env = ExecutorEnv::builder()
        .write(&(product_id, name_bytes, input.volume))
        .unwrap()
        .build()
        .unwrap();

    let prover = default_prover();
    let prove_info = prover.prove(env, GUEST_CODE_FOR_ZK_PROOF_ELF).unwrap();
    let receipt = prove_info.receipt;

    // Decode journal from receipt
    let journal: (u32, [u8; MAX_STR_LEN], u32, bool, [u8; MAX_STR_LEN]) =
        receipt.journal.decode().unwrap();

    // Only change certified 
    let product = Product {
        id: journal.0,
        name: bytes_to_string(&journal.1),
        volume: journal.2,
        certified: true,  // force certified to true
        sender: bytes_to_string(&journal.4),
    };

    // Serialize the proof to bytes and base64 after
    let receipt_bytes = bincode::serialize(&receipt).unwrap();
    let proof_b64 = general_purpose::STANDARD.encode(&receipt_bytes);

    let output = serde_json::json!({
        "product": product,
        "proof": proof_b64
    });
    println!("{}", output);

    receipt.verify(GUEST_CODE_FOR_ZK_PROOF_ID).unwrap();
}
