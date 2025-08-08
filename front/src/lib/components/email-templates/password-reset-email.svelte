<script lang="ts">
	export let reset_link: string;
	export let user_name: string;
	export let company_name = "Wagtee";
	export let expiry_hours = "1"; // How long the link is valid
</script>

<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
	<!-- Header -->
	<div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 40px 30px; text-align: center;">
		<h1 style="color: #ffffff; font-size: 28px; font-weight: bold; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
			{company_name}
		</h1>
		<p style="color: #fef0f0; font-size: 16px; margin: 10px 0 0 0; opacity: 0.9;">
			منصة الحجوزات الذكية
		</p>
	</div>

	<!-- Content -->
	<div style="padding: 40px 30px; background-color: #ffffff;">
		<!-- Warning Icon -->
		<div style="text-align: center; margin-bottom: 30px;">
			<div style="width: 80px; height: 80px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center;">
				<svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
					<path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
			</div>
			<h2 style="color: #2d3748; font-size: 24px; font-weight: bold; margin: 0 0 10px 0;">
				طلب إعادة تعيين كلمة المرور
			</h2>
			<p style="color: #718096; font-size: 16px; margin: 0; line-height: 1.6;">
				مرحباً <strong>{user_name}</strong>، تلقينا طلباً لإعادة تعيين كلمة المرور لحسابك.
			</p>
		</div>

		<!-- Reset Button -->
		<div style="text-align: center; margin: 40px 0;">
			<a href="{reset_link}" 
			   style="display: inline-block; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: #ffffff; text-decoration: none; padding: 16px 32px; border-radius: 50px; font-size: 16px; font-weight: bold; box-shadow: 0 4px 15px rgba(240, 147, 251, 0.4); transition: all 0.3s ease;">
				إعادة تعيين كلمة المرور
			</a>
		</div>

		<!-- Alternative Link -->
		<div style="background-color: #f8f9fa; border-radius: 8px; padding: 20px; margin: 30px 0;">
			<p style="color: #4a5568; font-size: 14px; margin: 0 0 10px 0;">
				إذا لم يعمل الزر أعلاه، يمكنك نسخ ولصق الرابط التالي في متصفحك:
			</p>
			<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; word-break: break-all;">
				<a href="{reset_link}" style="color: #667eea; text-decoration: none; font-size: 12px;">
					{reset_link}
				</a>
			</div>
		</div>

		<!-- Expiry Notice -->
		<div style="background-color: #fffbeb; border: 1px solid #f6e05e; border-radius: 6px; padding: 15px; margin: 20px 0;">
			<p style="color: #b7791f; font-size: 13px; margin: 0; line-height: 1.5;">
				⏰ <strong>مهم:</strong> هذا الرابط صالح لمدة {expiry_hours} ساعة فقط. إذا انتهت صلاحية الرابط، يمكنك طلب رابط جديد.
			</p>
		</div>

		<!-- Security Notice -->
		<div style="background-color: #fff5f5; border: 1px solid #fed7d7; border-radius: 6px; padding: 15px; margin: 20px 0;">
			<h4 style="color: #c53030; font-size: 14px; margin: 0 0 10px 0;">🔒 ملاحظات أمنية مهمة:</h4>
			<ul style="color: #c53030; font-size: 13px; margin: 0; padding-right: 20px; line-height: 1.6;">
				<li>إذا لم تطلب إعادة تعيين كلمة المرور، يرجى تجاهل هذه الرسالة</li>
				<li>لا تشارك هذا الرابط مع أي شخص آخر</li>
				<li>تأكد من أنك تستخدم جهازاً آمناً عند إعادة تعيين كلمة المرور</li>
			</ul>
		</div>

		<!-- Help Section -->
		<div style="text-align: center; margin: 30px 0; padding: 20px; background-color: #f7fafc; border-radius: 8px;">
			<h3 style="color: #2d3748; font-size: 16px; margin: 0 0 10px 0;">تحتاج مساعدة؟</h3>
			<p style="color: #718096; font-size: 14px; margin: 0; line-height: 1.6;">
				إذا واجهت أي مشاكل أو لديك أسئلة، لا تتردد في التواصل معنا على:
			</p>
			<p style="margin: 10px 0 0 0;">
				<a href="mailto:support@wagtee.com" style="color: #667eea; text-decoration: none; font-weight: bold;">
					support@wagtee.com
				</a>
			</p>
		</div>
	</div>

	<!-- Footer -->
	<div style="background-color: #f7fafc; padding: 30px; text-align: center; border-top: 1px solid #e2e8f0;">
		<p style="color: #718096; font-size: 14px; margin: 0 0 10px 0;">
			هذه رسالة تلقائية، يرجى عدم الرد عليها.
		</p>
		
		<div style="margin: 20px 0;">
			<a href="#" style="display: inline-block; margin: 0 10px; text-decoration: none;">
				<img src="https://via.placeholder.com/24x24/f5576c/ffffff?text=T" alt="Twitter" style="width: 24px; height: 24px; border-radius: 50%;">
			</a>
			<a href="#" style="display: inline-block; margin: 0 10px; text-decoration: none;">
				<img src="https://via.placeholder.com/24x24/f5576c/ffffff?text=F" alt="Facebook" style="width: 24px; height: 24px; border-radius: 50%;">
			</a>
			<a href="#" style="display: inline-block; margin: 0 10px; text-decoration: none;">
				<img src="https://via.placeholder.com/24x24/f5576c/ffffff?text=I" alt="Instagram" style="width: 24px; height: 24px; border-radius: 50%;">
			</a>
		</div>

		<div style="border-top: 1px solid #e2e8f0; padding-top: 20px; margin-top: 20px;">
			<p style="color: #a0aec0; font-size: 12px; margin: 0; direction: rtl;">
				© 2025 Wagtee. جميع الحقوق محفوظة.<br>
				الرياض، المملكة العربية السعودية
			</p>
		</div>
	</div>
</div>