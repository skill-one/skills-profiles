# Solidity 安全

掌握智能合约安全最佳实践、漏洞预防以及安全的 Solidity 开发模式。

## 何时使用这项技能

- 编写安全的智能合约
- 审计现有合约以查找漏洞
- 实施安全的 DeFi 协议
- 防止重入、溢出和访问控制问题
- 在保持安全的同时优化 gas 使用
- 为专业审计准备合约
- 了解常见的攻击向量

## 详细模式和实例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。

## 安全测试

```javascript
// Hardhat 测试示例
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("安全测试", function () {
  it("应防止重入攻击", async function () {
    const [attacker] = await ethers.getSigners();

    const VictimBank = await ethers.getContractFactory("SecureBank");
    const bank = await VictimBank.deploy();

    const Attacker = await ethers.getContractFactory("ReentrancyAttacker");
    const attackerContract = await Attacker.deploy(bank.address);

    // 存入资金
    await bank.deposit({ value: ethers.utils.parseEther("10") });

    // 尝试重入攻击
    await expect(
      attackerContract.attack({ value: ethers.utils.parseEther("1") }),
    ).to.be.revertedWith("ReentrancyGuard: reentrant call");
  });

  it("应防止整数溢出", async function () {
    const Token = await ethers.getContractFactory("SecureToken");
    const token = await Token.deploy();

    // 尝试溢出
    await expect(token.transfer(attacker.address, ethers.constants.MaxUint256))
      .to.be.reverted;
  });

  it("应执行访问控制", async function () {
    const [owner, attacker] = await ethers.getSigners();

    const Contract = await ethers.getContractFactory("SecureContract");
    const contract = await Contract.deploy();

    // 尝试未授权的提款
    await expect(contract.connect(attacker).withdraw(100)).to.be.revertedWith(
      "Ownable: caller is not the owner",
    );
  });
});
```

## 审计准备

```solidity
contract WellDocumentedContract {
    /**
     * @title Well Documented Contract
     * @dev 审计的适当文档示例
     * @notice 该合约处理用户存款和提款
     */

    /// @notice 用户余额映射
    mapping(address => uint256) public balances;

    /**
     * @dev 向合约存入 ETH
     * @notice 任何人都可以存入资金
     */
    function deposit() public payable {
        require(msg.value > 0, "Must send ETH");
        balances[msg.sender] += msg.value;
    }

    /**
     * @dev 提款用户的余额
     * @notice 遵循 CEI 模式以防止重入
     * @param amount 要提款的金额（wei）
     */
    function withdraw(uint256 amount) public {
        // 检查
        require(amount <= balances[msg.sender], "Insufficient balance");

        // 效果
        balances[msg.sender] -= amount;

        // 交互
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
    }
}
```
