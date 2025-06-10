"""
快速修复 Gradio 兼容性问题的脚本
直接修复 main_browser_use.py 中的启动问题
"""

def fix_gradio_launch():
    """修复 Gradio 启动问题"""
    import os
    
    # 读取 main_browser_use.py
    main_file = "main_browser_use.py"
    
    if not os.path.exists(main_file):
        print(f"❌ 找不到文件: {main_file}")
        return False
    
    try:
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换有问题的启动代码
        old_launch = """demo.launch(
            server_name="127.0.0.1",
            server_port=7899,
            share=False,
            debug=False,
            show_error=True,
            enable_queue=True
        )"""
        
        new_launch = """# 兼容不同版本的 Gradio
        try:
            demo.launch(
                server_name="127.0.0.1",
                server_port=7899,
                share=False,
                show_error=True
            )
        except TypeError as e:
            if "unexpected keyword argument" in str(e):
                # 兼容旧版本参数
                demo.launch(
                    server_name="127.0.0.1",
                    server_port=7899,
                    share=False
                )
            else:
                raise"""
        
        # 执行替换
        if "enable_queue=True" in content:
            content = content.replace(old_launch, new_launch)
            
            # 保存修复后的文件
            with open(main_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Gradio 兼容性问题已修复!")
            print(f"🔧 已更新文件: {main_file}")
            return True
        else:
            print("⚠️ 文件中未找到需要修复的代码")
            return False
            
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 修复 Gradio 兼容性问题")
    print("=" * 40)
    
    if fix_gradio_launch():
        print("\n✅ 修复完成!")
        print("🚀 现在可以重新启动系统:")
        print("   python main_browser_use.py")
        print("   或")
        print("   python start.bat")
    else:
        print("\n❌ 修复失败")
        print("💡 建议直接运行:")
        print("   python simple_run.py")

if __name__ == "__main__":
    main()