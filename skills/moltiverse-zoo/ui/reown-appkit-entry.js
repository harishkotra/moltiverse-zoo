import { createAppKit } from "@reown/appkit";
import { WagmiAdapter } from "@reown/appkit-adapter-wagmi";
import { getWalletClient, watchAccount } from "@wagmi/core";
import { defineChain } from "viem";

let modal = null;
let wagmiConfig = null;
let hasInitialized = false;
let isAuthenticating = false;

function buildMonadChain(rpcUrl, chainId) {
  return defineChain({
    id: chainId,
    name: "Monad Mainnet",
    network: "monad",
    nativeCurrency: {
      name: "Monad",
      symbol: "MON",
      decimals: 18,
    },
    rpcUrls: {
      default: { http: [rpcUrl] },
      public: { http: [rpcUrl] },
    },
    blockExplorers: {
      default: {
        name: "Monad Explorer",
        url: "https://explorer.monad.xyz",
      },
    },
  });
}

function getMetadata() {
  return {
    name: "Moltiverse Zoo",
    description: "Moltiverse Zoo Command Center",
    url: window.location.origin,
    icons: [],
  };
}

window.initReownAppKit = function initReownAppKit(config = {}) {
  console.log("initReownAppKit called with config:", config);
  if (hasInitialized) {
    console.log("Already initialized, skipping");
    return;
  }

  const projectId = (config.reownProjectId || "").trim();
  if (!projectId) {
    console.warn("Reown project ID missing");
    return;
  }

  console.log("Initializing Reown AppKit with projectId:", projectId);

  const rpcUrl = (config.monadRpcUrl || "https://rpc.monad.xyz").trim();
  const chainId = Number(config.monadChainId || 143);

  const monad = buildMonadChain(rpcUrl, chainId);

  const wagmiAdapter = new WagmiAdapter({
    projectId,
    networks: [monad],
  });

  wagmiConfig = wagmiAdapter.wagmiConfig;

  modal = createAppKit({
    adapters: [wagmiAdapter],
    networks: [monad],
    projectId,
    metadata: getMetadata(),
    features: {
      analytics: false,
    },
  });

  console.log("Reown AppKit modal created successfully");

  watchAccount(wagmiConfig, {
    onChange: async (account) => {
      if (!account.isConnected || !account.address || isAuthenticating) return;
      if (!window.zooAuth) return;

      isAuthenticating = true;
      try {
        if (window.showStatus) {
          window.showStatus("Wallet connected! Creating challenge...", "success");
        }

        const challenge = await window.zooAuth.requestChallenge(account.address);

        if (window.showStatus) {
          window.showStatus("Please sign the message in your wallet...", "info");
        }

        const walletClient = await getWalletClient(wagmiConfig);
        const signature = await walletClient.signMessage({ message: challenge });

        if (window.showStatus) {
          window.showStatus("Verifying signature...", "info");
        }

        await window.zooAuth.verifySignature(account.address, signature);
      } catch (error) {
        console.error("Reown authentication error:", error);
        if (window.showStatus) {
          window.showStatus(`Error: ${error.message || "Authentication failed"}`, "error");
        }
      } finally {
        isAuthenticating = false;
      }
    },
  });

  hasInitialized = true;
  console.log("Reown AppKit initialization complete");
};

window.zooConnectWallet = async function zooConnectWallet() {
  if (!modal) {
    throw new Error("Wallet connector not ready");
  }
  await modal.open();
};
