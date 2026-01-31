// 四个项目的完整 Mock 数据
const projectsData = {
    "Azuki": {
        twitter: "@AzukiEN",
        website: "azuki.com",
        contract: "0xed5af38865e05c81cb826c3742787055585c19f2",
        score: 78,
        riskLevel: "high",
        riskLabel: "严重画饼",
        dimensions: {
            integrity: {
                score: 32,
                weight: 30,
                label: "诚信",
                level: "low",
                explanation: "10条承诺中仅3条兑现，诚信得分偏低"
            },
            fairness: {
                score: 55,
                weight: 20,
                label: "公平性",
                level: "medium",
                explanation: "NFT分布中度集中，Top 10持有约35%"
            },
            development: {
                score: 41,
                weight: 20,
                label: "开发力",
                level: "low",
                explanation: "GitHub活跃度下降，近6个月平均月提交8次"
            },
            finance: {
                score: 72,
                weight: 15,
                label: "财务",
                level: "high",
                explanation: "国库资金相对稳定，当前余额127 ETH"
            },
            momentum: {
                score: 58,
                weight: 15,
                label: "动能",
                level: "medium",
                explanation: "Twitter活跃度一般，周均推文约12条"
            }
        },
        promisesStats: {
            total: 15,
            fulfilled: 3,
            unfulfilled: 12,
            unverifiable: 0
        },
        timeline: [
            { date: "2025-01-30", score: 78, integrityScore: 32, status: "verified", summary: "完成验证，画饼指数 78（高风险）" },
            { date: "2024-10-15", score: 65, integrityScore: 45, status: "verified", summary: "完成验证，画饼指数 65（中高风险）" },
            { date: "2024-06-20", score: 52, integrityScore: 56, status: "verified", summary: "完成验证，画饼指数 52（中风险）" },
            { date: "2024-02-01", score: 38, integrityScore: 72, status: "verified", summary: "首次验证，画饼指数 38（低风险）" }
        ]
    },

    "Moonbirds": {
        twitter: "@moonbirds",
        website: "moonbirds.xyz",
        contract: "0x23581767a106ae21c074b2276d25e5c3e136a68b",
        score: 54,
        riskLevel: "medium",
        riskLabel: "中度画饼",
        dimensions: {
            integrity: {
                score: 58,
                weight: 30,
                label: "诚信",
                level: "medium",
                explanation: "7条承诺中3条未兑现，诚信表现一般"
            },
            fairness: {
                score: 62,
                weight: 20,
                label: "公平性",
                level: "medium",
                explanation: "NFT分布较为分散，Top 10持有约28%"
            },
            development: {
                score: 48,
                weight: 20,
                label: "开发力",
                level: "low",
                explanation: "GitHub活跃度中等，近6个月平均月提交12次"
            },
            finance: {
                score: 55,
                weight: 15,
                label: "财务",
                level: "medium",
                explanation: "国库资金波动较大，当前余额89 ETH"
            },
            momentum: {
                score: 51,
                weight: 15,
                label: "动能",
                level: "medium",
                explanation: "Twitter活跃度中等，周均推文约8条"
            }
        },
        promisesStats: {
            total: 10,
            fulfilled: 3,
            unfulfilled: 7,
            unverifiable: 0
        },
        timeline: [
            { date: "2025-01-28", score: 54, integrityScore: 58, status: "verified", summary: "完成验证，画饼指数 54（中风险）" },
            { date: "2024-09-10", score: 48, integrityScore: 62, status: "verified", summary: "完成验证，画饼指数 48（中低风险）" },
            { date: "2024-05-15", score: 42, integrityScore: 68, status: "verified", summary: "首次验证，画饼指数 42（低风险）" }
        ]
    },

    "Pudgy Penguins": {
        twitter: "@PudgyPenguins",
        website: "pudgypenguins.com",
        contract: "0xbd3531da5cf5857e7cfaa92426877b022e612cf8",
        score: 23,
        riskLevel: "low",
        riskLabel: "可信",
        dimensions: {
            integrity: {
                score: 82,
                weight: 30,
                label: "诚信",
                level: "high",
                explanation: "9条承诺中7条已兑现，诚信表现优秀"
            },
            fairness: {
                score: 75,
                weight: 20,
                label: "公平性",
                level: "high",
                explanation: "NFT分布非常分散，Top 10持有约18%"
            },
            development: {
                score: 68,
                weight: 20,
                label: "开发力",
                level: "medium",
                explanation: "GitHub活跃度良好，近6个月平均月提交18次"
            },
            finance: {
                score: 78,
                weight: 15,
                label: "财务",
                level: "high",
                explanation: "国库资金稳定增长，当前余额245 ETH"
            },
            momentum: {
                score: 72,
                weight: 15,
                label: "动能",
                level: "high",
                explanation: "Twitter活跃度高，周均推文约18条"
            }
        },
        promisesStats: {
            total: 9,
            fulfilled: 7,
            unfulfilled: 2,
            unverifiable: 0
        },
        timeline: [
            { date: "2025-01-25", score: 23, integrityScore: 82, status: "verified", summary: "完成验证，画饼指数 23（低风险）" },
            { date: "2024-08-20", score: 28, integrityScore: 78, status: "verified", summary: "完成验证，画饼指数 28（低风险）" },
            { date: "2024-04-10", score: 32, integrityScore: 75, status: "verified", summary: "首次验证，画饼指数 32（低风险）" }
        ]
    },

    "CloneX": {
        twitter: "@clonex",
        website: "clonex.rtfkt.com",
        contract: "0x49cf6f5d44e70224e2e23fdcdd2c053f30ada28b",
        score: 71,
        riskLevel: "high",
        riskLabel: "严重画饼",
        dimensions: {
            integrity: {
                score: 41,
                weight: 30,
                label: "诚信",
                level: "low",
                explanation: "13条承诺中仅4条兑现，诚信得分较低"
            },
            fairness: {
                score: 58,
                weight: 20,
                label: "公平性",
                level: "medium",
                explanation: "NFT分布中度集中，Top 10持有约32%"
            },
            development: {
                score: 52,
                weight: 20,
                label: "开发力",
                level: "medium",
                explanation: "GitHub活跃度一般，近6个月平均月提交10次"
            },
            finance: {
                score: 65,
                weight: 15,
                label: "财务",
                level: "medium",
                explanation: "国库资金较为稳定，当前余额156 ETH"
            },
            momentum: {
                score: 48,
                weight: 15,
                label: "动能",
                level: "low",
                explanation: "Twitter活跃度下降，周均推文约6条"
            }
        },
        promisesStats: {
            total: 13,
            fulfilled: 4,
            unfulfilled: 9,
            unverifiable: 0
        },
        timeline: [
            { date: "2025-01-27", score: 71, integrityScore: 41, status: "verified", summary: "完成验证，画饼指数 71（高风险）" },
            { date: "2024-10-05", score: 68, integrityScore: 45, status: "verified", summary: "完成验证，画饼指数 68（中高风险）" },
            { date: "2024-06-01", score: 58, integrityScore: 52, status: "verified", summary: "首次验证，画饼指数 58（中风险）" }
        ]
    }
};

// 计算���达图坐标的辅助函数
function calculateRadarCoordinates(dimensions) {
    const center = { x: 150, y: 150 };
    const radius = 120;

    // 五边形顶点坐标（相对于中心点的向量）
    const vertices = {
        integrity: { x: 0, y: -120 },      // 诚信（顶部）
        fairness: { x: 114, y: -37 },      // 公平性（右上）
        finance: { x: 70, y: 97 },         // 财务（右下）
        momentum: { x: -70, y: 97 },       // 动能（左下）
        development: { x: -114, y: -37 }   // 开发力（左上）
    };

    const coords = {};
    const points = [];

    // 按照五边形顶点顺序计算坐标
    const order = ['integrity', 'fairness', 'finance', 'momentum', 'development'];

    order.forEach(key => {
        const dim = dimensions[key];
        const vertex = vertices[key];
        const score = dim.score / 100;

        const x = Math.round(center.x + vertex.x * score);
        const y = Math.round(center.y + vertex.y * score);

        coords[key] = { x, y };
        points.push(`${x},${y}`);
    });

    return {
        coords,
        pointsString: points.join(' ')
    };
}

// 获取项目数据
function getProjectData(projectName) {
    return projectsData[projectName] || projectsData["Azuki"];
}
