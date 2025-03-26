package com.moonciki.cursorsekiro;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.TimeUnit;
import org.json.JSONObject;
import java.util.UUID;

/**
 * Cursor设备ID修改工具 - Java版本
 * 用于重置Cursor编辑器的设备标识
 */
public class CursorReset {
    // ANSI颜色代码
    private static final String RED = "\u001B[31m";
    private static final String GREEN = "\u001B[32m";
    private static final String YELLOW = "\u001B[33m";
    private static final String BLUE = "\u001B[34m";
    private static final String RESET = "\u001B[0m";

    // 文件路径
    private static final String APPDATA = System.getenv("APPDATA");
    private static final String STORAGE_FILE = APPDATA + "\\Cursor\\User\\globalStorage\\storage.json";
    private static final String BACKUP_DIR = APPDATA + "\\Cursor\\User\\globalStorage\\backups";
    private static final String CURSOR_PATH = System.getenv("LOCALAPPDATA") + "\\Programs\\cursor";

    /**
     * 主方法
     */
    public static void main(String[] args) {
        try {
            // 设置控制台编码为UTF-8
            System.setProperty("file.encoding", "UTF-8");
            
            // 检查管理员权限
            if (!isAdmin()) {
                System.out.println(RED + "[错误]" + RESET + " 请以管理员身份运行此程序");
                restartAsAdmin();
                System.exit(1);
            }

            // 检查Cursor版本
            checkCursorVersion();

            // 关闭Cursor进程
            killCursorProcesses();

            // 创建备份目录
            createBackupDirectory();

            // 备份当前配置
            backupConfiguration();

            // 生成新的ID
            String machineId = generateMachineId();
            String macMachineId = UUID.randomUUID().toString();
            String devDeviceId = UUID.randomUUID().toString();
            String sqmId = "{" + UUID.randomUUID().toString().toUpperCase() + "}";

            // 更新配置文件
            updateConfiguration(machineId, macMachineId, devDeviceId, sqmId);

            // 更新注册表
            updateMachineGuid();

            // 显示结果
            displayResults(machineId, macMachineId, devDeviceId, sqmId);

            // 询问是否禁用自动更新
            handleAutoUpdate();

        } catch (Exception e) {
            System.out.println(RED + "[错误]" + RESET + " 程序执行失败: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * 以管理员权限重启程序
     */
    private static void restartAsAdmin() {
        try {
            String javaBin = System.getProperty("java.home") + File.separator + "bin" + File.separator + "java";
            String currentJar = new File(CursorReset.class.getProtectionDomain().getCodeSource().getLocation().toURI()).getPath();
            
            ProcessBuilder pb = new ProcessBuilder(
                "cmd", "/c",
                "powershell", "Start-Process",
                "-FilePath", javaBin,
                "-ArgumentList", "'-jar','" + currentJar + "'",
                "-Verb", "RunAs"
            );
            pb.start();
        } catch (Exception e) {
            System.out.println(RED + "[错误]" + RESET + " 无法以管理员权限重启: " + e.getMessage());
        }
    }

    /**
     * 检查是否具有管理员权限
     */
    private static boolean isAdmin() {
        try {
            ProcessBuilder pb = new ProcessBuilder("cmd.exe", "/c", "net session");
            pb.redirectErrorStream(true);
            Process p = pb.start();
            p.waitFor();
            return p.exitValue() == 0;
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * 检查Cursor版本
     */
    private static void checkCursorVersion() {
        try {
            Path packagePath = Paths.get(CURSOR_PATH, "resources", "app", "package.json");
            if (Files.exists(packagePath)) {
                String content = new String(Files.readAllBytes(packagePath));
                JSONObject json = new JSONObject(content);
                System.out.println(GREEN + "[信息]" + RESET + " 当前安装的 Cursor 版本: v" + json.getString("version"));
            } else {
                System.out.println(YELLOW + "[警告]" + RESET + " 无法检测到 Cursor 版本");
            }
        } catch (Exception e) {
            System.out.println(RED + "[错误]" + RESET + " 获取 Cursor 版本失败: " + e.getMessage());
        }
    }

    /**
     * 关闭Cursor进程
     */
    private static void killCursorProcesses() throws Exception {
        System.out.println(GREEN + "[信息]" + RESET + " 检查 Cursor 进程...");
        ProcessBuilder pb = new ProcessBuilder("taskkill", "/F", "/IM", "Cursor.exe");
        pb.redirectErrorStream(true);
        Process p = pb.start();
        p.waitFor(5, TimeUnit.SECONDS);
    }

    /**
     * 创建备份目录
     */
    private static void createBackupDirectory() throws IOException {
        Files.createDirectories(Paths.get(BACKUP_DIR));
    }

    /**
     * 备份配置文件
     */
    private static void backupConfiguration() throws IOException {
        Path sourcePath = Paths.get(STORAGE_FILE);
        if (Files.exists(sourcePath)) {
            String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
            Path backupPath = Paths.get(BACKUP_DIR, "storage.json.backup_" + timestamp);
            Files.copy(sourcePath, backupPath, StandardCopyOption.REPLACE_EXISTING);
        }
    }

    /**
     * 生成新的MachineId
     */
    private static String generateMachineId() {
        String prefix = "auth0|user_";
        byte[] randomBytes = new byte[32];
        new Random().nextBytes(randomBytes);
        StringBuilder sb = new StringBuilder();
        for (byte b : prefix.getBytes(StandardCharsets.UTF8)) {
            sb.append(String.format("%02x", b));
        }
        for (byte b : randomBytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }

    /**
     * 更新配置文件，使用更安全的方式处理JSON
     */
    private static void updateConfiguration(String machineId, String macMachineId,
                                         String devDeviceId, String sqmId) throws IOException {
        Path configPath = Paths.get(STORAGE_FILE);
        Path tempFile = null;
        
        try {
            // 创建临时文件
            tempFile = Files.createTempFile("cursor_config_", ".tmp");
            
            // 读取原始配置
            String content = new String(Files.readAllBytes(configPath), StandardCharsets.UTF8);
            JSONObject config = new JSONObject(content);
            
            // 备份原始值
            JSONObject backup = new JSONObject();
            backup.put("telemetry.machineId", config.optString("telemetry.machineId"));
            backup.put("telemetry.macMachineId", config.optString("telemetry.macMachineId"));
            backup.put("telemetry.devDeviceId", config.optString("telemetry.devDeviceId"));
            backup.put("telemetry.sqmId", config.optString("telemetry.sqmId"));
            
            // 更新配置
            config.put("telemetry.machineId", machineId);
            config.put("telemetry.macMachineId", macMachineId);
            config.put("telemetry.devDeviceId", devDeviceId);
            config.put("telemetry.sqmId", sqmId);
            
            // 先写入临时文件
            Files.write(tempFile, config.toString(2).getBytes(StandardCharsets.UTF8));
            
            // 验证JSON格式
            new JSONObject(new String(Files.readAllBytes(tempFile), StandardCharsets.UTF8));
            
            // 替换原文件
            Files.move(tempFile, configPath, StandardCopyOption.REPLACE_EXISTING);
            
        } catch (Exception e) {
            System.out.println(RED + "[错误]" + RESET + " 更新配置失败: " + e.getMessage());
            // 如果有临时文件，清理它
            if (tempFile != null) {
                try {
                    Files.deleteIfExists(tempFile);
                } catch (IOException ignored) {}
            }
            throw e;
        }
    }

    /**
     * 改进的MachineGuid更新方法
     */
    private static void updateMachineGuid() throws Exception {
        String guid = UUID.randomUUID().toString();
        String registryPath = "SOFTWARE\\Microsoft\\Cryptography";
        
        // 备份当前值
        ProcessBuilder backupPb = new ProcessBuilder(
            "reg",
            "export",
            "HKLM\\" + registryPath,
            BACKUP_DIR + "\\MachineGuid_" + 
                LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss")) + ".reg"
        );
        
        Process backupProcess = backupPb.start();
        if (backupProcess.waitFor() == 0) {
            System.out.println(GREEN + "[信息]" + RESET + " 已备份注册表值");
        }
        
        // 更新值
        ProcessBuilder pb = new ProcessBuilder(
            "reg",
            "add",
            "HKLM\\" + registryPath,
            "/v",
            "MachineGuid",
            "/t",
            "REG_SZ",
            "/d",
            guid,
            "/f"
        );
        
        Process p = pb.start();
        if (p.waitFor() != 0) {
            throw new Exception("更新注册表失败");
        }
        
        // 验证更新
        ProcessBuilder verifyPb = new ProcessBuilder(
            "reg",
            "query",
            "HKLM\\" + registryPath,
            "/v",
            "MachineGuid"
        );
        
        Process verifyProcess = verifyPb.start();
        if (verifyProcess.waitFor() == 0) {
            System.out.println(GREEN + "[信息]" + RESET + " 已成功更新注册表");
        }
    }

    /**
     * 显示操作结果
     */
    private static void displayResults(String machineId, String macMachineId,
                                     String devDeviceId, String sqmId) {
        System.out.println("\n" + GREEN + "[信息]" + RESET + " 已更新配置:");
        System.out.println(BLUE + "[调试]" + RESET + " machineId: " + machineId);
        System.out.println(BLUE + "[调试]" + RESET + " macMachineId: " + macMachineId);
        System.out.println(BLUE + "[调试]" + RESET + " devDeviceId: " + devDeviceId);
        System.out.println(BLUE + "[调试]" + RESET + " sqmId: " + sqmId);
    }

    /**
     * 处理自动更新设置
     */
    private static void handleAutoUpdate() throws Exception {
        System.out.println("\n" + YELLOW + "[询问]" + RESET + " 是否要禁用 Cursor 自动更新功能？");
        System.out.println("0) 否 - 保持默认设置");
        System.out.println("1) 是 - 禁用自动更新");

        Scanner scanner = new Scanner(System.in);
        String choice = scanner.nextLine();

        if ("1".equals(choice)) {
            String updaterPath = System.getenv("LOCALAPPDATA") + "\\cursor-updater";
            Files.write(Paths.get(updaterPath), new byte[0]);
            Files.setAttribute(Paths.get(updaterPath), "dos:readonly", true);
            System.out.println(GREEN + "[信息]" + RESET + " 已禁用自动更新");
        }
    }
}