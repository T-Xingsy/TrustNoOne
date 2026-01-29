/**
 * On-Chain Verifier - 核心实现
 *
 * 基于 ethers.js v6 的链上数据查询和验证工具
 * 用于 Promise Breaker Detector 项目
 */

import { ethers, Contract, Provider, JsonRpcProvider } from 'ethers';

export interface VerifierConfig {
  rpcUrl: string;
  contractAddress: string;
  contractABI: any[];
  chainId?: number;
  fallbackRpcUrl?: string;
  timeout?: number;
}

export interface TransferEvent {
  from: string;
  to: string;
  tokenId: bigint;
  blockNumber: number;
  transactionHash: string;
  timestamp: number;
  eventType: 'mint' | 'transfer' | 'burn';
}

export interface AirdropVerification {
  totalAmount: number;
  uniqueRecipients: number;
  transactions: TransferEvent[];
  fulfillmentRate: number;
  evidenceStrength: 'strong' | 'moderate' | 'weak' | 'none';
  summary: string;
}

export class OnChainVerifier {
  private provider: JsonRpcProvider;
  private contract: Contract;
  private config: VerifierConfig;

  constructor(config: VerifierConfig) {
    this.config = config;
    this.provider = new ethers.JsonRpcProvider(config.rpcUrl);
    this.contract = new Contract(
      config.contractAddress,
      config.contractABI,
      this.provider
    );
  }

  /**
   * 查询 Transfer 事件
   */
  async queryTransferEvents(params: {
    startTime?: Date;
    endTime?: Date;
    startBlock?: number;
    endBlock?: number;
    from?: string;
    to?: string;
    eventType?: 'mint' | 'transfer' | 'burn' | 'all';
  }): Promise<TransferEvent[]> {
    // 1. 转换时间为区块号
    let startBlock = params.startBlock;
    let endBlock = params.endBlock;

    if (params.startTime && !startBlock) {
      startBlock = await this.getBlockByTimestamp(params.startTime);
    }

    if (params.endTime && !endBlock) {
      endBlock = await this.getBlockByTimestamp(params.endTime);
    }

    // 2. 构建事件过滤器
    const filter = this.buildTransferFilter(params);

    // 3. 查询事件
    const events = await this.contract.queryFilter(
      filter,
      startBlock,
      endBlock
    );

    // 4. 解析事件
    const transfers: TransferEvent[] = [];
    for (const event of events) {
      const transfer = await this.parseTransferEvent(event);
      transfers.push(transfer);
    }

    return transfers;
  }

  /**
   * 验证空投承诺
   */
  async verifyAirdropPromise(params: {
    promise: any;
    projectAddress: string;
    startTime: Date;
    endTime: Date;
    minBatchSize?: number;
  }): Promise<AirdropVerification> {
    const minBatchSize = params.minBatchSize || 5;

    // 1. 查询从项目方地址发出的转账
    const transfers = await this.queryTransferEvents({
      startTime: params.startTime,
      endTime: params.endTime,
      from: params.projectAddress,
      eventType: 'transfer',
    });

    // 2. 识别空投交易（批量转账）
    const airdropTxs = this.identifyAirdropTransactions(
      transfers,
      minBatchSize
    );

    // 3. 统计数据
    const uniqueRecipients = new Set(airdropTxs.map(t => t.to)).size;
    const totalAmount = airdropTxs.length;

    // 4. 计算履约率
    const expectedAmount = params.promise.expectedAmount || 0;
    const fulfillmentRate = expectedAmount > 0
      ? (totalAmount / expectedAmount) * 100
      : 0;

    // 5. 评估证据强度
    const evidenceStrength = this.assessEvidenceStrength(
      totalAmount,
      uniqueRecipients,
      fulfillmentRate
    );

    // 6. 生成摘要
    const summary = `Found ${totalAmount} airdrop transaction(s) to ${uniqueRecipients} unique recipient(s)`;

    return {
      totalAmount,
      uniqueRecipients,
      transactions: airdropTxs,
      fulfillmentRate,
      evidenceStrength,
      summary,
    };
  }

  /**
   * 获取合约统计信息
   */
  async getContractStatistics(): Promise<{
    totalSupply: number;
    totalMinted: number;
    totalBurned: number;
    uniqueHolders: number;
  }> {
    // 实现统计逻辑
    // TODO: 实现完整的统计功能
    throw new Error('Not implemented yet');
  }

  /**
   * 格式化为 LLM 上下文
   */
  async formatForLLM(params: {
    promise: any;
    onchainData: AirdropVerification;
    mode: 'full' | 'compact' | 'scoring';
  }): Promise<string> {
    if (params.mode === 'compact') {
      return this.formatCompact(params.promise, params.onchainData);
    } else if (params.mode === 'scoring') {
      return this.formatForScoring(params.promise, params.onchainData);
    } else {
      return this.formatFull(params.promise, params.onchainData);
    }
  }

  // ==================== 私有方法 ====================

  private async getBlockByTimestamp(timestamp: Date): Promise<number> {
    // 二分查找最接近的区块
    // TODO: 实现二分查找算法
    const currentBlock = await this.provider.getBlockNumber();
    return currentBlock - 1000; // 临时实现
  }

  private buildTransferFilter(params: any) {
    const { from, to, eventType } = params;

    if (eventType === 'mint') {
      return this.contract.filters.Transfer(ethers.ZeroAddress, to, null);
    } else if (eventType === 'burn') {
      return this.contract.filters.Transfer(from, ethers.ZeroAddress, null);
    } else {
      return this.contract.filters.Transfer(from, to, null);
    }
  }

  private async parseTransferEvent(event: any): Promise<TransferEvent> {
    const block = await this.provider.getBlock(event.blockNumber);

    let eventType: 'mint' | 'transfer' | 'burn';
    if (event.args.from === ethers.ZeroAddress) {
      eventType = 'mint';
    } else if (event.args.to === ethers.ZeroAddress) {
      eventType = 'burn';
    } else {
      eventType = 'transfer';
    }

    return {
      from: event.args.from,
      to: event.args.to,
      tokenId: event.args.tokenId,
      blockNumber: event.blockNumber,
      transactionHash: event.transactionHash,
      timestamp: block!.timestamp,
      eventType,
    };
  }

  private identifyAirdropTransactions(
    transfers: TransferEvent[],
    minBatchSize: number
  ): TransferEvent[] {
    // 按交易哈希分组
    const txGroups = new Map<string, TransferEvent[]>();

    for (const transfer of transfers) {
      const txHash = transfer.transactionHash;
      if (!txGroups.has(txHash)) {
        txGroups.set(txHash, []);
      }
      txGroups.get(txHash)!.push(transfer);
    }

    // 筛选批量交易
    const airdropTxs: TransferEvent[] = [];
    for (const [_, group] of txGroups) {
      if (group.length >= minBatchSize) {
        airdropTxs.push(...group);
      }
    }

    return airdropTxs;
  }

  private assessEvidenceStrength(
    totalAmount: number,
    uniqueRecipients: number,
    fulfillmentRate: number
  ): 'strong' | 'moderate' | 'weak' | 'none' {
    if (totalAmount === 0) return 'none';
    if (fulfillmentRate >= 80 && uniqueRecipients >= 100) return 'strong';
    if (fulfillmentRate >= 50 && uniqueRecipients >= 50) return 'moderate';
    return 'weak';
  }

  private formatFull(promise: any, data: AirdropVerification): string {
    return `
=== PROMISE ===
Content: ${promise.content}
Deadline: ${promise.deadline}

=== ON-CHAIN EVIDENCE ===
Transactions Found: ${data.totalAmount}
Unique Recipients: ${data.uniqueRecipients}
Fulfillment Rate: ${data.fulfillmentRate.toFixed(1)}%
Evidence Strength: ${data.evidenceStrength}

Summary: ${data.summary}

=== PRELIMINARY ANALYSIS ===
${this.generateAnalysis(promise, data)}
    `.trim();
  }

  private formatCompact(promise: any, data: AirdropVerification): string {
    return `Promise: ${promise.content}\nEvidence: ${data.totalAmount} txs, ${data.uniqueRecipients} recipients, ${data.fulfillmentRate.toFixed(0)}% fulfilled`;
  }

  private formatForScoring(promise: any, data: AirdropVerification): string {
    return `
=== SCORING CONTEXT ===
Promise: ${promise.content}
Evidence: ${data.totalAmount} transactions, ${data.uniqueRecipients} recipients
Fulfillment: ${data.fulfillmentRate.toFixed(1)}%
Strength: ${data.evidenceStrength}
    `.trim();
  }

  private generateAnalysis(promise: any, data: AirdropVerification): string {
    const timing = data.fulfillmentRate > 0 ? 'Completed' : 'Not completed';
    const coverage = `${data.uniqueRecipients} recipients`;
    const overall = data.evidenceStrength === 'strong'
      ? 'Strong evidence - likely fulfilled'
      : data.evidenceStrength === 'moderate'
      ? 'Moderate evidence - partially fulfilled'
      : 'Weak evidence - likely not fulfilled';

    return `Timing: ${timing}\nCoverage: ${coverage}\nOverall: ${overall}`;
  }
}

// ==================== 导出 ====================

export default OnChainVerifier;
